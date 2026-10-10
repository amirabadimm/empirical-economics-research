"""Persian management brief with Amiri and explicit RTL/LTR typesetting."""
from asset_allocation.build_reit_latex_report import ROOT, read

REPORT = ROOT / "reports/REIT_MANAGEMENT_BRIEF_FA.tex"
FUNDS = {"Arzesh Maskan": "ارزش مسکن", "Kelid": "کلید", "Danik": "دانیک"}


def number(value, places=1, signed=False, percent=False):
    text = format(value, f"{'+' if signed else ''}.{places}f")
    text = text.translate(str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫"))
    return r"\lr{" + text + ("٪" if percent else "") + "}"


def table(headers, rows):
    # XePersian's RTL context places the first logical column at the right.
    return (r"\begin{RTL}\begin{center}\small\renewcommand{\arraystretch}{1.6}" + "\n"
            + r"\begin{tabular}{" + "|" + "c|" * len(headers) + "}\n"
            + r"\hline " + " & ".join(headers) + r" \\ \hline" + "\n"
            + "\n".join(" & ".join(row) + r" \\ \hline" for row in rows)
            + "\n" + r"\end{tabular}\end{center}\end{RTL}")


def build():
    grid = read("reit_requested_correlation_heatmaps.csv")
    mix = read("reit_codal_asset_mix_monthly.csv")

    def corr(fund, benchmark, frequency, window, lag=0):
        rows = grid.loc[grid.fund.eq(fund) & grid.benchmark.eq(benchmark)
                        & grid.frequency.eq(frequency) & grid.window_months.eq(window)
                        & grid.lag_weeks.eq(lag)]
        if len(rows) != 1 or rows.iloc[0].status != "reported":
            raise ValueError("Management brief needs one reported correlation per requested cell")
        return number(rows.iloc[0].correlation, 2, signed=True)

    summary_rows = [[name, corr(fund, "Tehran housing", "monthly", 24),
                     corr(fund, "TEDPIX", "monthly", 24), corr(fund, "USD/IRR", "daily", 3)]
                    for fund, name in FUNDS.items()]
    lag_rows = [[name, *(corr(fund, "USD/IRR leads REIT", "weekly", 24, lag)
                         for lag in (4, 13, 26))] for fund, name in FUNDS.items()]
    allocation_rows = []
    paragraphs = []
    for fund in ("Arzesh Maskan", "Danik"):
        s = mix.loc[mix.fund.eq(fund)].sort_values("jalali_period")
        first, last = s.iloc[0], s.iloc[-1]
        p = lambda x: number(100*x, percent=True)
        allocation_rows.append([FUNDS[fund], p(first.housing_share), p(last.housing_share),
                                p(s.housing_share.mean()), p(last.fixed_income_share),
                                p(last.other_including_cash_equity_share)])
        paragraphs.append(r"\textbf{" + FUNDS[fund] + "، ترکیب دارایی‌ها.} "
                          + "سهم ملک از " + p(first.housing_share) + " در ابتدای دوره به "
                          + p(last.housing_share) + " در پایان دوره رسیده است. میانگین سهم ملک "
                          + p(s.housing_share.mean()) + " و کمترین مقدار آن " + p(s.housing_share.min())
                          + " بوده است. در پایان دوره، " + p(1-last.housing_share)
                          + " از دارایی‌ها ملک نبوده؛ شامل " + p(last.fixed_income_share)
                          + " درآمد ثابت و " + p(last.other_including_cash_equity_share) + " سایر دارایی‌ها."
                          + (" سهم درآمد ثابت در مقطعی به " + p(s.fixed_income_share.max())
                             + " رسیده است؛ بنابراین دانیک در بخش‌هایی از دوره، عمدتاً صندوقی با دارایی غیرملکی بوده است."
                             if fund == "Danik" else ""))
    parts = [r"\documentclass[12pt,a4paper]{article}",
             r"\usepackage[margin=2cm]{geometry}", r"\usepackage{array}",
             r"\usepackage{xepersian}", r"\settextfont{Amiri}",
             r"\setlatintextfont{Amiri}", r"\setdigitfont{Amiri}",
             r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.5em}",
             r"\linespread{1.12}", r"\begin{document}",
             r"{\Large\bfseries گزارش مدیریتی صندوق‌های املاک و مستغلات}\par",
             "ارزش مسکن، کلید و دانیک؛ بررسی وضعیت تا مهر ۱۴۰۵",
             r"\textbf{جمع‌بندی.} در دوره بررسی‌شده، تغییرات بازده این صندوق‌ها همراهی ضعیفی با تغییرات قیمت مسکن داشته است. رابطه با بورس مثبت‌تر و روشن‌تر بوده، به‌ویژه برای کلید. ارتباط با دلار نیز در همه افق‌ها یکسان نیست و شواهد، دنباله‌روی قوی و منظم صندوق‌ها از دلار را نشان نمی‌دهد. همچنین بخش قابل توجهی از دارایی‌های ارزش مسکن و دانیک، ملک نبوده است؛ این موضوع در مورد دانیک برجسته‌تر است.",
             r"\textbf{رابطه با مسکن و بورس.} در بررسی دوساله، همبستگی ماهانه با مسکن برای ارزش مسکن و کلید نزدیک صفر و برای دانیک ضعیف و منفی است. در همان دوره و با همان مقیاس ماهانه، رابطه با شاخص کل بورس برای هر سه صندوق مثبت بوده و در کلید قوی‌تر از دو صندوق دیگر است. در نتیجه، رفتار قیمت واحدهای این صندوق‌ها را نمی‌توان معادل رفتار قیمت مسکن دانست.",
             r"\textbf{رابطه با دلار.} در سه ماه اخیر، همبستگی روزانه با دلار برای هر سه صندوق منفی و نسبتاً ضعیف بوده است. در بررسی دوساله نیز رابطه بازده صندوق‌ها با تغییرات دلار در حدود یک، سه و شش ماه قبل، ضعیف و منفی است. بررسی جداگانه فاصله‌های کوتاه‌تر، یک تا دو هفته، نشانه‌هایی از رابطه مثبت نشان می‌دهد؛ اما قدرت توضیح‌دهندگی آن محدود است. بنابراین نتیجه را نباید به «بی‌ارتباطی کامل» یا «تبعیت قابل اتکا از دلار» تعبیر کرد.",
             *paragraphs,
             r"\textbf{برداشت مدیریتی.} عنوان صندوق املاک، به‌تنهایی تضمین‌کننده سرمایه‌گذاری عمده و مستمر در ملک یا همراهی بازده با مسکن نیست. در دوره بررسی‌شده، کلید و دانیک برای کسب مواجهه قابل اتکا با رشد قیمت مسکن عملکرد مناسبی نداشته‌اند. ارزش مسکن از نظر بازده نهایی بهتر بوده، اما همراهی ماهانه آن با مسکن نیز ضعیف است. ترکیب دارایی ارزش مسکن و دانیک ضرورت بررسی تصمیم‌های تخصیص دارایی را نشان می‌دهد؛ تعیین سهم ضعف مدیریت در نتیجه به تفکیک اثر عوامل نیاز دارد.",
             r"\newpage", r"{\Large\bfseries جداول پشتیبان}\par",
             r"\textbf{جدول ۱ ـ همبستگی بازده صندوق‌ها با مسکن، بورس و دلار}",
             table(["صندوق", "مسکن", "شاخص کل بورس", "دلار"], summary_rows),
             "مسکن و بورس: بازده ماهانه در دو سال اخیر؛ دلار: بازده روزانه در سه ماه اخیر. "
             "مثبت یعنی حرکت هم‌جهت، منفی یعنی حرکت خلاف‌جهت و نزدیک صفر یعنی همراهی اندک. به‌دلیل تفاوت دوره و مقیاس زمانی، ستون دلار مستقیماً با دو ستون دیگر قابل مقایسه نیست.",
             r"\textbf{جدول ۲ ـ همبستگی با تغییرات قبلی دلار در دوره دوساله}",
             table(["صندوق", "حدود یک ماه قبل", "حدود سه ماه قبل", "حدود شش ماه قبل"], lag_rows),
             "این جدول نشان می‌دهد بازده هفتگی صندوق تا چه اندازه با تغییرات قبلی دلار همراه بوده است؛ ارقام، اثر قطعی دلار را اندازه‌گیری نمی‌کنند.",
             r"\textbf{جدول ۳ ـ سهم ملک و سایر دارایی‌ها در ارزش مسکن و دانیک}",
             table(["صندوق", "ملک ابتدا", "ملک پایان", "میانگین ملک", "درآمد ثابت پایان", "سایر پایان"], allocation_rows),
             "دوره ترکیب دارایی‌ها از مهر ۱۴۰۳ تا شهریور ۱۴۰۵ است. «سایر» شامل وجه نقد، سهام و سایر دارایی‌ها و مطالبات است؛ در دانیک، بخش عمده آن در پایان دوره در سرفصل سایر دارایی‌ها و مطالبات قرار دارد. این ارقام سهم دارایی‌های صندوق هستند، نه سهمی از تعداد واحدهای آن.",
             r"\textbf{مبنای گزارش.} محاسبات پروژه و اطلاعات گردآوری‌شده از کدال مبنا قرار گرفته است. معیار مسکن، تغییر قیمت پیشنهادی مسکن تهران در داده‌های کیلید است. بازده صندوق‌ها با لحاظ سودهای نقدی ثبت‌شده و فرض خرید مجدد واحدها در نخستین روز معاملاتی از تاریخ مجمع محاسبه شده است. اطلاعات ترکیب دارایی بر اساس دسته‌بندی و بازسازی ارائه‌شده در فایل کدال است.",
             r"\end{document}"]
    REPORT.write_text("\n\n".join(parts)+"\n", encoding="utf-8")
    return REPORT


if __name__ == "__main__":
    print(build())
