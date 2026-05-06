# Results

```
$ uv run devpost stats
Rows per (model × hackathon)                                                                                                                                                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ model                                  ┃ cal-hacks-12-0 ┃ hackgt-12 ┃ madhacks ┃ madhacks-fall-2025 ┃ pennapps-xxv ┃ treehacks-2024 ┃ treehacks-2025 ┃ treehacks-2026 ┃  TOTAL ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507            │              — │     3,500 │      580 │              1,200 │        1,080 │          4,194 │          3,100 │          4,954 │ 18,608 │
│ Qwen/Qwen3.5-27B                       │         12,926 │     3,500 │      580 │              1,200 │        1,080 │          4,194 │          3,100 │          4,942 │ 31,522 │
│ Qwen/Qwen3.5-4B                        │         12,926 │     3,500 │      580 │              1,200 │        1,080 │          4,194 │          3,100 │          4,942 │ 31,522 │
│ openai/gpt-oss-20b                     │          6,931 │     3,500 │      580 │              1,200 │        1,080 │          4,194 │          3,100 │          4,954 │ 25,539 │
│ twangodev/devpost-hacks-qwen3-4b-judge │         12,936 │     3,500 │      580 │              1,200 │        1,080 │          4,194 │          3,100 │          4,954 │ 31,544 │
└────────────────────────────────────────┴────────────────┴───────────┴──────────┴────────────────────┴──────────────┴────────────────┴────────────────┴────────────────┴────────┘

Verdict distribution per judge                                                                              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━┳━━━━━━┓
┃ model                                  ┃      A ┃      B ┃   tie ┃ invalid ┃    A% ┃    B% ┃ tie% ┃ inv% ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━╇━━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507            │  7,679 │ 10,929 │     0 │       0 │ 41.3% │ 58.7% │ 0.0% │ 0.0% │
│ Qwen/Qwen3.5-27B                       │ 17,632 │ 13,235 │     0 │     655 │ 55.9% │ 42.0% │ 0.0% │ 2.1% │
│ Qwen/Qwen3.5-4B                        │ 15,089 │ 15,302 │     3 │   1,128 │ 47.9% │ 48.5% │ 0.0% │ 3.6% │
│ openai/gpt-oss-20b                     │ 12,460 │ 12,880 │    47 │     152 │ 48.8% │ 50.4% │ 0.2% │ 0.6% │
│ twangodev/devpost-hacks-qwen3-4b-judge │ 15,882 │ 12,943 │ 1,733 │     986 │ 50.3% │ 41.0% │ 5.5% │ 3.1% │
└────────────────────────────────────────┴────────┴────────┴───────┴─────────┴───────┴───────┴──────┴──────┘

Position consistency (A/B vs B/A picks same project)                                                          
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ model                                  ┃  pairs ┃  agree ┃  flip ┃ inv-1 ┃ inv-2 ┃ consistency ┃ flip rate ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ Qwen/Qwen3.5-4B                        │ 15,761 │ 12,817 │ 1,851 │ 1,056 │    37 │       87.4% │     12.6% │
│ openai/gpt-oss-20b                     │ 12,764 │ 10,848 │ 1,718 │   198 │     0 │       86.3% │     13.7% │
│ twangodev/devpost-hacks-qwen3-4b-judge │ 15,772 │ 11,171 │ 2,001 │ 2,579 │    21 │       84.8% │     15.2% │
│ Qwen/Qwen3.5-27B                       │ 15,761 │ 12,151 │ 2,965 │   635 │    10 │       80.4% │     19.6% │
│ Qwen/Qwen3-4B-Instruct-2507            │  9,304 │  6,967 │ 2,337 │     0 │     0 │       74.9% │     25.1% │
└────────────────────────────────────────┴────────┴────────┴───────┴───────┴───────┴─────────────┴───────────┘

Latency + token stats per judge                                                                                                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ model                                  ┃      n ┃ median compl tok ┃ p95 compl tok ┃ median lat s ┃ p95 lat s ┃ truncated % ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507            │ 18,608 │            1,192 │         1,446 │         36.3 │      53.0 │       0.00% │
│ Qwen/Qwen3.5-27B                       │ 31,522 │            2,763 │         5,270 │        190.9 │     355.1 │       0.56% │
│ Qwen/Qwen3.5-4B                        │ 31,522 │            3,434 │         7,565 │         60.7 │     133.2 │       3.61% │
│ openai/gpt-oss-20b                     │ 25,539 │              769 │         1,556 │         53.7 │     173.0 │       0.00% │
│ twangodev/devpost-hacks-qwen3-4b-judge │ 31,544 │            2,953 │         8,192 │        124.6 │     349.6 │      16.36% │
└────────────────────────────────────────┴────────┴──────────────────┴───────────────┴──────────────┴───────────┴─────────────┘
```

```
$ uv run devpost summary --bootstrap 1000
Loading held-out test pair_ids (cs639 split, seed=42)...
Eval scope: held-out test set (2430 pair_ids)  ·  39 (hackathon × judge) combos  ·  B=1000  ·  workers=24

(148.0s)

Per (hackathon × judge) — point estimate + 95% bootstrap CI                                                                
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ hackathon          ┃ model                  ┃  top-1  ┃   recall@1 [95% CI] ┃  recall@10 [95% CI] ┃ median pct [95% CI] ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ cal-hacks-12-0     │ Qwen/Qwen3.5-27B       │ ✗ (24%) │ 0.002 [0.000–0.010] │ 0.021 [0.000–0.040] │ 0.364 [0.308–0.408] │
│ cal-hacks-12-0     │ Qwen/Qwen3.5-4B        │ ✗ (26%) │ 0.003 [0.000–0.010] │ 0.023 [0.000–0.040] │ 0.368 [0.310–0.414] │
│ cal-hacks-12-0     │ openai/gpt-oss-20b     │ ✓ (54%) │ 0.005 [0.000–0.010] │ 0.028 [0.010–0.050] │ 0.400 [0.324–0.469] │
│ cal-hacks-12-0     │ twangodev/devpost-hac… │ ✗ (22%) │ 0.002 [0.000–0.010] │ 0.021 [0.000–0.040] │ 0.368 [0.310–0.426] │
│ hackgt-12          │ Qwen/Qwen3-4B-Instruc… │ ✗ (14%) │ 0.006 [0.000–0.040] │ 0.040 [0.000–0.080] │ 0.358 [0.265–0.458] │
│ hackgt-12          │ Qwen/Qwen3.5-27B       │ ✗ (18%) │ 0.007 [0.000–0.040] │ 0.057 [0.000–0.120] │ 0.329 [0.230–0.417] │
│ hackgt-12          │ Qwen/Qwen3.5-4B        │ ✓ (24%) │ 0.010 [0.000–0.040] │ 0.061 [0.000–0.120] │ 0.338 [0.226–0.446] │
│ hackgt-12          │ openai/gpt-oss-20b     │ ✗ (17%) │ 0.007 [0.000–0.040] │ 0.065 [0.000–0.160] │ 0.310 [0.219–0.393] │
│ hackgt-12          │ twangodev/devpost-hac… │ ✗ (4%)  │ 0.001 [0.000–0.040] │ 0.034 [0.000–0.080] │ 0.302 [0.210–0.388] │
│ madhacks           │ Qwen/Qwen3-4B-Instruc… │ ✗ (22%) │ 0.022 [0.000–0.100] │ 0.148 [0.000–0.300] │ 0.473 [0.357–0.600] │
│ madhacks           │ Qwen/Qwen3.5-27B       │ ✓ (36%) │ 0.036 [0.000–0.100] │ 0.141 [0.000–0.300] │ 0.578 [0.366–0.750] │
│ madhacks           │ Qwen/Qwen3.5-4B        │ ✗ (3%)  │ 0.003 [0.000–0.100] │ 0.129 [0.000–0.300] │ 0.595 [0.405–0.775] │
│ madhacks           │ openai/gpt-oss-20b     │ ✗ (11%) │ 0.011 [0.000–0.100] │ 0.182 [0.000–0.400] │ 0.470 [0.237–0.722] │
│ madhacks           │ twangodev/devpost-hac… │ ✗ (12%) │ 0.012 [0.000–0.100] │ 0.177 [0.000–0.300] │ 0.511 [0.308–0.707] │
│ madhacks-fall-2025 │ Qwen/Qwen3-4B-Instruc… │ ✗ (6%)  │ 0.005 [0.000–0.077] │ 0.138 [0.000–0.308] │ 0.443 [0.200–0.639] │
│ madhacks-fall-2025 │ Qwen/Qwen3.5-27B       │ ✗ (7%)  │ 0.005 [0.000–0.077] │ 0.123 [0.000–0.231] │ 0.479 [0.240–0.667] │
│ madhacks-fall-2025 │ Qwen/Qwen3.5-4B        │ ✗ (8%)  │ 0.006 [0.000–0.077] │ 0.110 [0.000–0.231] │ 0.507 [0.264–0.676] │
│ madhacks-fall-2025 │ openai/gpt-oss-20b     │ ✗ (11%) │ 0.008 [0.000–0.077] │ 0.160 [0.000–0.308] │ 0.460 [0.164–0.685] │
│ madhacks-fall-2025 │ twangodev/devpost-hac… │ ✗ (5%)  │ 0.004 [0.000–0.077] │ 0.131 [0.000–0.231] │ 0.442 [0.211–0.671] │
│ pennapps-xxv       │ Qwen/Qwen3-4B-Instruc… │ ✗ (39%) │ 0.016 [0.000–0.040] │ 0.176 [0.080–0.240] │ 0.279 [0.187–0.368] │
│ pennapps-xxv       │ Qwen/Qwen3.5-27B       │ ✓ (60%) │ 0.024 [0.000–0.040] │ 0.159 [0.080–0.240] │ 0.346 [0.238–0.432] │
│ pennapps-xxv       │ Qwen/Qwen3.5-4B        │ ✓ (66%) │ 0.027 [0.000–0.040] │ 0.201 [0.120–0.280] │ 0.266 [0.171–0.355] │
│ pennapps-xxv       │ openai/gpt-oss-20b     │ ✓ (81%) │ 0.032 [0.000–0.040] │ 0.146 [0.080–0.240] │ 0.342 [0.243–0.431] │
│ pennapps-xxv       │ twangodev/devpost-hac… │ ✗ (38%) │ 0.015 [0.000–0.040] │ 0.170 [0.080–0.240] │ 0.319 [0.207–0.418] │
│ treehacks-2024     │ Qwen/Qwen3-4B-Instruc… │ ✗ (20%) │ 0.003 [0.000–0.017] │ 0.058 [0.017–0.103] │ 0.380 [0.297–0.487] │
│ treehacks-2024     │ Qwen/Qwen3.5-27B       │ ✗ (20%) │ 0.003 [0.000–0.017] │ 0.045 [0.017–0.086] │ 0.401 [0.320–0.485] │
│ treehacks-2024     │ Qwen/Qwen3.5-4B        │ ✗ (25%) │ 0.004 [0.000–0.017] │ 0.060 [0.017–0.103] │ 0.324 [0.253–0.393] │
│ treehacks-2024     │ openai/gpt-oss-20b     │ ✗ (35%) │ 0.006 [0.000–0.017] │ 0.060 [0.017–0.103] │ 0.348 [0.272–0.432] │
│ treehacks-2024     │ twangodev/devpost-hac… │ ✗ (15%) │ 0.003 [0.000–0.017] │ 0.044 [0.017–0.086] │ 0.355 [0.288–0.430] │
│ treehacks-2025     │ Qwen/Qwen3-4B-Instruc… │ ✓ (56%) │ 0.008 [0.000–0.014] │ 0.062 [0.029–0.100] │ 0.366 [0.305–0.426] │
│ treehacks-2025     │ Qwen/Qwen3.5-27B       │ ✗ (29%) │ 0.004 [0.000–0.014] │ 0.050 [0.014–0.086] │ 0.388 [0.315–0.457] │
│ treehacks-2025     │ Qwen/Qwen3.5-4B        │ ✗ (39%) │ 0.006 [0.000–0.014] │ 0.061 [0.029–0.100] │ 0.389 [0.308–0.454] │
│ treehacks-2025     │ openai/gpt-oss-20b     │ ✗ (47%) │ 0.007 [0.000–0.014] │ 0.061 [0.029–0.086] │ 0.389 [0.322–0.459] │
│ treehacks-2025     │ twangodev/devpost-hac… │ ✗ (29%) │ 0.004 [0.000–0.014] │ 0.052 [0.028–0.086] │ 0.379 [0.305–0.451] │
│ treehacks-2026     │ Qwen/Qwen3-4B-Instruc… │ ✗ (51%) │ 0.008 [0.000–0.016] │ 0.069 [0.032–0.113] │ 0.362 [0.273–0.436] │
│ treehacks-2026     │ Qwen/Qwen3.5-27B       │ ✗ (34%) │ 0.005 [0.000–0.016] │ 0.053 [0.016–0.097] │ 0.369 [0.293–0.445] │
│ treehacks-2026     │ Qwen/Qwen3.5-4B        │ ✗ (28%) │ 0.005 [0.000–0.016] │ 0.056 [0.016–0.097] │ 0.317 [0.243–0.394] │
│ treehacks-2026     │ openai/gpt-oss-20b     │ ✗ (40%) │ 0.006 [0.000–0.016] │ 0.067 [0.032–0.113] │ 0.324 [0.249–0.395] │
│ treehacks-2026     │ twangodev/devpost-hac… │ ✗ (23%) │ 0.004 [0.000–0.016] │ 0.041 [0.000–0.081] │ 0.393 [0.316–0.462] │
└────────────────────┴────────────────────────┴─────────┴─────────────────────┴─────────────────────┴─────────────────────┘

Aggregate across 8 hackathons (paired by hackathon)                                            
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ model                    ┃ top-1 hit rate ┃ mean recall@1 ┃ mean recall@10 ┃ mean recall@50 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ Qwen/Qwen3-4B-Instruct-… │    1/7 = 14.3% │         0.002 │          0.091 │          0.409 │
│ Qwen/Qwen3.5-27B         │    2/8 = 25.0% │         0.018 │          0.075 │          0.367 │
│ Qwen/Qwen3.5-4B          │    2/8 = 25.0% │         0.010 │          0.088 │          0.404 │
│ openai/gpt-oss-20b       │    2/8 = 25.0% │         0.006 │          0.093 │          0.388 │
│ twangodev/devpost-hacks… │     0/8 = 0.0% │         0.000 │          0.095 │          0.389 │
└──────────────────────────┴────────────────┴───────────────┴────────────────┴────────────────┘
Pairwise judge comparisons (median across shared hackathons)                                                                
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
┃ judge A                     ┃ judge B                      ┃ N hacks ┃ median ρ ┃ median τ ┃ McNemar p ┃ A-only / B-only ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-27B             │       7 │   +0.784 │   +0.623 │     1.000 │           1 / 2 │
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-4B              │       7 │   +0.807 │   +0.631 │     1.000 │           1 / 2 │
│ Qwen/Qwen3-4B-Instruct-2507 │ openai/gpt-oss-20b           │       7 │   +0.816 │   +0.641 │     1.000 │           1 / 1 │
│ Qwen/Qwen3-4B-Instruct-2507 │ twangodev/devpost-hacks-qwe… │       7 │   +0.810 │   +0.642 │     1.000 │           1 / 0 │
│ Qwen/Qwen3.5-27B            │ Qwen/Qwen3.5-4B              │       8 │   +0.861 │   +0.711 │     1.000 │           1 / 1 │
│ Qwen/Qwen3.5-27B            │ openai/gpt-oss-20b           │       8 │   +0.795 │   +0.638 │     1.000 │           1 / 1 │
│ Qwen/Qwen3.5-27B            │ twangodev/devpost-hacks-qwe… │       8 │   +0.911 │   +0.765 │     0.500 │           2 / 0 │
│ Qwen/Qwen3.5-4B             │ openai/gpt-oss-20b           │       8 │   +0.828 │   +0.650 │     1.000 │           1 / 1 │
│ Qwen/Qwen3.5-4B             │ twangodev/devpost-hacks-qwe… │       8 │   +0.845 │   +0.677 │     0.500 │           2 / 0 │
│ openai/gpt-oss-20b          │ twangodev/devpost-hacks-qwe… │       8 │   +0.811 │   +0.629 │     0.500 │           2 / 0 │
└─────────────────────────────┴──────────────────────────────┴─────────┴──────────┴──────────┴───────────┴─────────────────┘
Paired Wilcoxon — recall@10 (cross-hackathon)                                                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━┓
┃ judge A                     ┃ judge B                      ┃ N ┃  med Δ ┃ mean Δ ┃     p ┃ sig ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-27B             │ 7 │ +0.000 │ +0.009 │ 0.250 │     │
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-4B              │ 7 │ +0.000 │ -0.007 │ 0.500 │     │
│ Qwen/Qwen3-4B-Instruct-2507 │ openai/gpt-oss-20b           │ 7 │ +0.000 │ -0.011 │ 0.875 │     │
│ Qwen/Qwen3-4B-Instruct-2507 │ twangodev/devpost-hacks-qwe… │ 7 │ +0.000 │ -0.014 │ 1.000 │     │
│ Qwen/Qwen3.5-27B            │ Qwen/Qwen3.5-4B              │ 8 │ -0.007 │ -0.014 │ 0.125 │     │
│ Qwen/Qwen3.5-27B            │ openai/gpt-oss-20b           │ 8 │ -0.017 │ -0.019 │ 0.219 │     │
│ Qwen/Qwen3.5-27B            │ twangodev/devpost-hacks-qwe… │ 8 │ +0.000 │ -0.020 │ 0.500 │     │
│ Qwen/Qwen3.5-4B             │ openai/gpt-oss-20b           │ 8 │ -0.012 │ -0.005 │ 0.281 │     │
│ Qwen/Qwen3.5-4B             │ twangodev/devpost-hacks-qwe… │ 8 │ +0.015 │ -0.006 │ 0.797 │     │
│ openai/gpt-oss-20b          │ twangodev/devpost-hacks-qwe… │ 8 │ +0.014 │ -0.001 │ 0.797 │     │
└─────────────────────────────┴──────────────────────────────┴───┴────────┴────────┴───────┴─────┘
Paired Wilcoxon — recall@50 (cross-hackathon)                                                     
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━┳━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━┓
┃ judge A                     ┃ judge B                      ┃ N ┃  med Δ ┃ mean Δ ┃     p ┃ sig ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━╇━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━┩
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-27B             │ 7 │ +0.014 │ +0.004 │ 0.438 │     │
│ Qwen/Qwen3-4B-Instruct-2507 │ Qwen/Qwen3.5-4B              │ 7 │ -0.034 │ -0.037 │ 0.031 │ **  │
│ Qwen/Qwen3-4B-Instruct-2507 │ openai/gpt-oss-20b           │ 7 │ +0.000 │ -0.020 │ 0.250 │     │
│ Qwen/Qwen3-4B-Instruct-2507 │ twangodev/devpost-hacks-qwe… │ 7 │ +0.000 │ -0.020 │ 0.375 │     │
│ Qwen/Qwen3.5-27B            │ Qwen/Qwen3.5-4B              │ 8 │ -0.030 │ -0.037 │ 0.031 │ **  │
│ Qwen/Qwen3.5-27B            │ openai/gpt-oss-20b           │ 8 │ +0.000 │ -0.021 │ 0.250 │     │
│ Qwen/Qwen3.5-27B            │ twangodev/devpost-hacks-qwe… │ 8 │ -0.019 │ -0.022 │ 0.094 │  ·  │
│ Qwen/Qwen3.5-4B             │ openai/gpt-oss-20b           │ 8 │ +0.005 │ +0.016 │ 0.500 │     │
│ Qwen/Qwen3.5-4B             │ twangodev/devpost-hacks-qwe… │ 8 │ +0.000 │ +0.015 │ 0.250 │     │
│ openai/gpt-oss-20b          │ twangodev/devpost-hacks-qwe… │ 8 │ -0.005 │ -0.001 │ 0.781 │     │
└─────────────────────────────┴──────────────────────────────┴───┴────────┴────────┴───────┴─────┘

Madhacks PL eval (paired bootstrap, B=1000, workers=24)...
MAP                                            1% 0:00:01 logp = -275.72, ||grad|| = 0.068114
Madhacks-fall-2025: judge BT vs human PL  (N=113 projects, 600      
pairs)                                                              
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ model                                  ┃     Spearman ρ [95% CI] ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ openai/gpt-oss-20b                     │ +0.335 [+0.291, +0.383] │
│ Qwen/Qwen3-4B-Instruct-2507            │ +0.334 [+0.289, +0.379] │
│ Qwen/Qwen3.5-4B                        │ +0.328 [+0.281, +0.372] │
│ twangodev/devpost-hacks-qwen3-4b-judge │ +0.307 [+0.252, +0.359] │
│ Qwen/Qwen3.5-27B                       │ +0.294 [+0.246, +0.337] │
└────────────────────────────────────────┴─────────────────────────┘
Distillation arc (paired Δρ)                            
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ comparison       ┃              Δρ [95% CI] ┃ P(Δ>0) ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ ft minus base    │ -0.0271 [-0.078, +0.021] │  12.9% │
│ ft minus teacher │ +0.0135 [-0.035, +0.063] │  71.5% │
└──────────────────┴──────────────────────────┴────────┘
MAP                                            1% 0:00:01 logp = -275.72, ||grad|| = 0.068114
Top 15 per judge — madhacks-fall-2025  (●=PL top-10  ✓=Devpost winner)                                                                                                
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ rank ┃ Human PL                 ┃ 2507 (base)              ┃ gpt-oss-20b              ┃ FT (4b-judge)            ┃ Qwen3.5-4B           ┃ Qwen3.5-27B              ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│    1 │ ● 3Docs                  │ PhishNet                 │ WhimsurAI                │ TrustRent                │ Janus                │ TrustRent                │
│    2 │ ● Collaboard             │ Line of Sight            │ TrustRent                │ ✓ Bird's I               │ TrustRent            │ Janus                    │
│    3 │ ● Factify                │ TrustRent                │ RiskChain                │ ● CV Crash Insurance     │ CallShield           │ ✓ Bird's I               │
│      │                          │                          │                          │ Fraud Detection          │                      │                          │
│    4 │ ● Lexon                  │ Janus                    │ CallShield               │ Rydr                     │ WhimsurAI            │ ● YATA_vioLin            │
│    5 │ ● Sub2Lease              │ CallShield               │ Janus                    │ ✓ StablePay              │ NoFi                 │ CallShield               │
│    6 │ ● Bucky's Buzzer Beater  │ ✓ StablePay              │ Line of Sight            │ Line of Sight            │ DevSpace             │ !You                     │
│    7 │ ● YATA_vioLin            │ Rydr                     │ ✓ Bird's I               │ Janus                    │ !You                 │ Rydr                     │
│    8 │ ● ChordSight             │ ● CV Crash Insurance     │ SquadPlanner             │ Baymax                   │ ✓ Bird's I           │ Baymax                   │
│      │                          │ Fraud Detection          │                          │                          │                      │                          │
│    9 │ ● CV Crash Insurance     │ WhimsurAI                │ DevSpace                 │ PhishNet                 │ ✓ Unsilenced         │ ✓ StablePay              │
│      │ Fraud Detection          │                          │                          │                          │                      │                          │
│   10 │ ● MindMerge              │ Baymax                   │ LucidCare                │ ● ChordSight             │ Replae               │ NoFi                     │
│   11 │ ● Sheet Diffusions       │ ✓ Unsilenced             │ Rydr                     │ ● YATA_vioLin            │ Line of Sight        │ PhishNet                 │
│   12 │ ● Lawly AI               │ !You                     │ !You                     │ !You                     │ ● YATA_vioLin        │ Spuddy                   │
│   13 │ ● Sentry                 │ RiskChain                │ Baymax                   │ WhimsurAI                │ Jarvis               │ RiskChain                │
│   14 │ ● Rydr                   │ Brainstormer             │ ● CV Crash Insurance     │ NoFi                     │ RiskChain            │ ● CV Crash Insurance     │
│      │                          │                          │ Fraud Detection          │                          │                      │ Fraud Detection          │
│   15 │ ● SquadSync              │ Replae                   │ ● Lexon                  │ Meridian                 │ Stellar Insight Labs │ LucidCare                │
└──────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────────┴──────────────────────┴──────────────────────────┘

PL top-K ∩ judge top-K (madhacks-fall-2025)                         
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ model         ┃      K=5 ┃       K=10 ┃       K=20 ┃        K=50 ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2507 (base)   │ 0/5 (0%) │ 1/10 (10%) │ 6/20 (30%) │ 28/50 (56%) │
│ gpt-oss-20b   │ 0/5 (0%) │  0/10 (0%) │ 5/20 (25%) │ 29/50 (58%) │
│ FT (4b-judge) │ 0/5 (0%) │ 2/10 (20%) │ 8/20 (40%) │ 27/50 (54%) │
│ Qwen3.5-4B    │ 0/5 (0%) │  0/10 (0%) │ 5/20 (25%) │ 27/50 (54%) │
│ Qwen3.5-27B   │ 0/5 (0%) │ 1/10 (10%) │ 5/20 (25%) │ 27/50 (54%) │
└───────────────┴──────────┴────────────┴────────────┴─────────────┘

Bottom 15 per judge — madhacks-fall-2025  (●=PL bottom-10  ✓=Devpost winner)                                                                                       
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ rank ┃ Human PL                 ┃ 2507 (base)            ┃ gpt-oss-20b              ┃ FT (4b-judge)           ┃ Qwen3.5-4B             ┃ Qwen3.5-27B            ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│   99 │ ● LeetBattles            │ BlueGuide              │ ● It's Movie Night       │ NicheCard               │ Voice Verse            │ RecipeAI               │
│  100 │ ● AIisa                  │ Mad Snacks             │ Urban Explorer's         │ ● NutriView             │ LeetBattles            │ ● NutriView            │
│      │                          │                        │ Nightmare                │                         │                        │                        │
│  101 │ ● ENHANCED ENROLL        │ Penni Personal Finance │ MindfulCompawnion        │ RecipeAI                │ ● NutriView            │ ● UncTracker           │
│  102 │ ● Lookout –              │ 6 7 Counter            │ ✓ Bob's Businesses       │ ● VocalDNA              │ ● UncTracker           │ Madison Marketplace    │
│      │ Community-Powered        │                        │                          │                         │                        │                        │
│      │ Emergency Safety App     │                        │                          │                         │                        │                        │
│  103 │ ● SpotShare              │ ● UncTracker           │ BlueGuide                │ Madison Marketplace     │ ● It's Movie Night     │ ✓ FocusMate            │
│  104 │ ● It's Movie Night       │ ● VocalDNA             │ ● NutriView              │ BlueGuide               │ RecipeAI               │ ClearMeet              │
│  105 │ ● VocalDNA               │ RecipeAI               │ 6G Conceptual Simulator  │ 6G Conceptual Simulator │ 6-7X Quantum Advantage │ Budget Besties         │
│  106 │ ● NeuroCursor            │ 6-7X Quantum Advantage │ 6-7X Quantum Advantage   │ Voice Verse             │ SafePlate              │ ✓ Bob's Businesses     │
│  107 │ ● Stellar Insight Labs   │ ● NutriView            │ SafePlate                │ ✓ Bob's Businesses      │ ConnectU               │ SafePlate              │
│  108 │ ● Recipe Manager         │ Budget Besties         │ Budget Besties           │ Gnostic                 │ Budget Besties         │ ● VocalDNA             │
│  109 │ ● FaunaVision            │ SafePlate              │ ● A-Meal                 │ Budget Besties          │ WhatsTheMove           │ 6-7X Quantum Advantage │
│  110 │ ● NoFi                   │ ✓ FocusMate            │ ✓ FocusMate              │ ● A-Meal                │ 6 7 Counter            │ WhatsTheMove           │
│  111 │ ● A-Meal                 │ WhatsTheMove           │ 6 7 Counter              │ WhatsTheMove            │ Gnostic                │ 6 7 Counter            │
│  112 │ ● NutriView              │ Voice Verse            │ WhatsTheMove             │ 6 7 Counter             │ ✓ FocusMate            │ Gnostic                │
│  113 │ ● UncTracker             │ ● A-Meal               │ Voice Verse              │ SafePlate               │ ● A-Meal               │ ● A-Meal               │
└──────┴──────────────────────────┴────────────────────────┴──────────────────────────┴─────────────────────────┴────────────────────────┴────────────────────────┘

PL bottom-K ∩ judge bottom-K (madhacks-fall-2025)                    
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ model         ┃       K=5 ┃       K=10 ┃       K=20 ┃        K=50 ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2507 (base)   │ 1/5 (20%) │ 3/10 (30%) │ 5/20 (25%) │ 28/50 (56%) │
│ gpt-oss-20b   │ 1/5 (20%) │ 2/10 (20%) │ 6/20 (30%) │ 29/50 (58%) │
│ FT (4b-judge) │ 1/5 (20%) │ 1/10 (10%) │ 6/20 (30%) │ 28/50 (56%) │
│ Qwen3.5-4B    │ 1/5 (20%) │ 1/10 (10%) │ 8/20 (40%) │ 28/50 (56%) │
│ Qwen3.5-27B   │ 1/5 (20%) │ 2/10 (20%) │ 5/20 (25%) │ 27/50 (54%) │
└───────────────┴───────────┴────────────┴────────────┴─────────────┘
```
