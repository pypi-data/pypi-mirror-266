# Latent
## Generating noise by GPU
`KSampler`

```python
latent = KSampler(model, seed, steps=20, cfg=5, latent_image=EmptyLatentImage(512, 800), scheduler=KSampler.scheduler.karras, sampler_name='uni_pc', positive=CLIPTextEncode(pos, clip), negative=CLIPTextEncode(neg, clip))
```

```python
# 
latent = BNKInjectNoise(EmptyLatentImage(512, 800), BNKGetSigma(model, sampler_name='uni_pc', steps=25), 1, noise=BNKNoisyLatentImage(BNKNoisyLatentImage.source.GPU, seed, 512, 800))
latent = KSamplerAdvanced(model, False, seed, steps=20, cfg=5, latent_image=latent, scheduler=KSampler.scheduler.karras, sampler_name='uni_pc', positive=CLIPTextEncode(pos, clip), negative=CLIPTextEncode(neg, clip))
```

[](https://github.com/BlenderNeko/ComfyUI_Noise)
```

```