import chevron

data = {
            "data": [
                    {
                        "folder": "folder1",
                        "log_1": 5,
                        "log_0_9": 5,
                        "log_0_8": 5,
                        "log_0_7": 5,
                        "log_0_6": 5,
                        "log_0_5": 5,
                        "log_0_4": 5,
                        "log_0_3": 3,
                        "log_0_2": 0,
                        "log_0_1": 0,
                        "log_0": 0,
                        "Total": 38
                    },
                    {
                        "folder": "folder2",
                        "log_1": 5,
                        "log_0_9": 5,
                        "log_0_8": 5,
                        "log_0_7": 5,
                        "log_0_6": 5,
                        "log_0_5": 5,
                        "log_0_4": 5,
                        "log_0_3": 3,
                        "log_0_2": 0,
                        "log_0_1": 0,
                        "log_0": 0,
                        "Total": 38
                    },
                    {
                        "folder": "folder3",
                        "log_1": 5,
                        "log_0_9": 5,
                        "log_0_8": 5,
                        "log_0_7": 5,
                        "log_0_6": 5,
                        "log_0_5": 5,
                        "log_0_4": 5,
                        "log_0_3": 3,
                        "log_0_2": 0,
                        "log_0_1": 0,
                        "log_0": 0,
                        "Total": 38
                    }
                ],
            "total": {
                "total_1": 30,
                "total_0_9": 30,
                "total_0_8": 30,
                "total_0_7": 30,
                "total_0_6": 30,
                "total_0_5": 30,
                "total_0_4": 30,
                "total_0_3": 30,
                "total_0_2": 30,
                "total_0_1": 30,
                "total_0": 30,
            }
        }

with open(r'C:\Users\zlin341\Documents\GitHub\okntool\okntool\sum_va_table_template.html', 'r') as f:
    fp = chevron.render(f, data)

with open(r'C:\Users\zlin341\Documents\GitHub\okntool\development\out2.html', 'w') as nf:
    nf.write(fp)
