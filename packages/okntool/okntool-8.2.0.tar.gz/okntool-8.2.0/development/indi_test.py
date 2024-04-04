import chevron

data = {"va": {"VA": 0.5, "bestline_VA": 0.4},
        "final_total": 40,
        "data": [
            {
                "logMAR": 1.0,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.9,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.8,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.7,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.6,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.5,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.4,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.3,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.2,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.1,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
            {
                "logMAR": 0.0,
                "trial_1_unicode": "&#x2713;",
                "trial_2_unicode": "&#x0058;",
                "trial_3_unicode": "&#x2713;",
                "trial_4_unicode": "&#x2713;",
                "trial_5_unicode": "&#x2713;",
                "Total": 4
            },
        ]
        }
with open(r'C:\Users\zlin341\Documents\GitHub\okntool\okntool\indi_va_table_template.html', 'r') as f:
    fp = chevron.render(f, data)

with open(r'C:\Users\zlin341\Documents\GitHub\okntool\development\out.html', 'w') as nf:
    nf.write(fp)

