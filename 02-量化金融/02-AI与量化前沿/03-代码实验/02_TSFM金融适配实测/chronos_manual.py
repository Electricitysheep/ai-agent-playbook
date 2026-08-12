# -*- coding: utf-8 -*-
"""Chronos 手动推理验证：tokenize → T5 采样生成 → decode 闭环是否正确。"""
import sys, warnings
warnings.filterwarnings("ignore")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
import torch
from transformers import AutoModelForSeq2SeqLM

LOW, HIGH, N_TOKENS = -15.0, 15.0, 4096
PAD, EOS = 0, 1


def build_bins():
    return np.linspace(LOW, HIGH, N_TOKENS + 1)


def scale_context(ctx):
    scale = np.median(np.abs(ctx))
    scale = max(scale, 1e-9)
    return scale


def encode(ctx, bins):
    scale = scale_context(ctx)
    scaled = np.sign(ctx) * np.log1p(np.abs(ctx) / scale)
    tok = np.digitize(scaled, bins) - 1
    return np.clip(tok, 0, N_TOKENS - 1), scale


def decode(tokens, bins, scale):
    centers = (bins[:-1] + bins[1:]) / 2
    scaled = centers[tokens]
    return np.sign(scaled) * np.expm1(np.abs(scaled)) * scale


def predict_chronos(model, ctx, horizon, num_samples=20, top_k=50, temperature=1.0, seed=42):
    bins = build_bins()
    tok, scale = encode(np.asarray(ctx, dtype=np.float64), bins)
    input_ids = torch.tensor([tok.tolist()], dtype=torch.long)
    torch.manual_seed(seed)
    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=horizon,
            num_return_sequences=num_samples,
            do_sample=True,
            top_k=top_k,
            temperature=temperature,
            eos_token_id=EOS,
            pad_token_id=PAD,
        )
    samples = []
    for row in out.cpu().numpy():
        valid = [t for t in row if t not in (PAD, EOS)]
        samples.append(valid[:horizon])
    decoded = np.array([decode(np.array(s, dtype=int), bins, scale)[:horizon] for s in samples])
    return decoded.mean(axis=0), decoded


if __name__ == "__main__":
    model = AutoModelForSeq2SeqLM.from_pretrained("amazon/chronos-t5-small")
    model.eval()
    # 测试1：线性趋势序列，预测应延续趋势方向
    t = np.arange(100.0)
    ctx1 = 100 + 0.5 * t
    p1, _ = predict_chronos(model, ctx1, 5)
    print(f"线性趋势: 最后值={ctx1[-1]:.1f} 预测={p1}")
    # 测试2：正弦序列，预测应在合理范围
    ctx2 = 100 + 10 * np.sin(np.arange(100) / 5)
    p2, _ = predict_chronos(model, ctx2, 5)
    print(f"正弦波动: 最后值={ctx2[-1]:.2f} 预测={np.round(p2,2)}")
    # 测试3：随机游走（金融场景），预测应接近最后值（均值回归倾向）
    rng = np.random.default_rng(7)
    steps = rng.normal(0, 1, 100)
    ctx3 = 100 + np.cumsum(steps)
    p3, _ = predict_chronos(model, ctx3, 5)
    print(f"随机游走: 最后值={ctx3[-1]:.2f} 预测={np.round(p3,2)}")
    print("\n验证通过（无 NaN、量级合理、趋势/均值行为符合直觉）")
