"""Detailed Persian report from the active research outputs."""
from datetime import date
import jdatetime
import pandas as pd

from asset_allocation.build_reit_latex_report import ROOT, read, GRID_SPECS
from asset_allocation.build_reit_management_brief_fa import number, table, FUNDS

REPORT = ROOT / "reports/REIT_DETAILED_REPORT_FA.tex"
NAMES = {**FUNDS, "Kakh": "کاخ", "TEDPIX": "شاخص کل بورس", "USD/IRR": "دلار",
         "Tehran housing": "مسکن تهران"}


def digits(text):
    return r"\lr{" + str(text).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")) + "}"


def jalali(text):
    d = jdatetime.date.fromgregorian(date=date.fromisoformat(str(text)))
    return digits(f"{d.year}/{d.month:02}/{d.day:02}")


def longtable(headers, rows):
    head = " & ".join(headers) + r" \\ \hline"
    return (r"\begin{RTL}\begingroup\small\renewcommand{\arraystretch}{1.4}" + "\n"
            + r"\begin{longtable}{|" + "c|" * len(headers) + "}\n"
            + r"\hline " + head + r"\endfirsthead" + "\n"
            + r"\hline " + head + r"\endhead" + "\n"
            + "\n".join(" & ".join(row) + r" \\ \hline" for row in rows)
            + "\n" + r"\end{longtable}\endgroup\end{RTL}")


def build():
    summary = read("reit_usd_tedpix_two_year_cumulative_summary.csv").set_index("asset")
    housing = read("tehran_housing_two_year_cumulative_summary.csv").iloc[0]
    mix = read("reit_codal_asset_mix_monthly.csv")
    grid = read("reit_requested_correlation_heatmaps.csv")
    events = read("reit_assembly_reinvestment_events.csv")
    daily = read("reit_assembly_reinvested_daily.csv")
    panel = read("reit_usd_tedpix_two_year_cumulative.csv")
    models = read("reit_usd_weekly_predictive_regressions.csv")
    p = lambda x: number(x*100, percent=True)
    signed = lambda x: number(x, 3, signed=True)
    parts = [r"\documentclass[12pt,a4paper]{article}",
             r"\usepackage[margin=2cm]{geometry}",
             r"\usepackage{array,longtable}", r"\usepackage{xepersian}",
             r"\settextfont{Amiri}\setlatintextfont{Amiri}\setdigitfont{Amiri}",
             r"\setlength{\parindent}{0pt}\setlength{\parskip}{0.5em}\linespread{1.1}",
             r"\begin{document}",
             r"{\LARGE\bfseries ارزیابی عملکرد صندوق‌های املاک و مستغلات}\par",
             "گزارش تحلیلی ارزش مسکن، کلید و دانیک؛ همراه با نتایج تکمیلی کاخ",
             "مبنای بررسی: آخرین داده‌های پروژه تا مهر ۱۴۰۵",
             r"\section*{جمع‌بندی مدیریتی}",
              "در دوره بررسی‌شده، این صندوق‌ها ابزار قابل اتکایی برای دنبال‌کردن تغییرات قیمت مسکن نبوده‌اند. کلید و دانیک، علاوه بر همراهی ضعیف با نوسانات مسکن، از نظر بازده تجمعی نیز فاصله قابل توجهی با معیار مسکن داشته‌اند. برای هدف مشخص کسب مواجهه با رشد قیمت مسکن، کارنامه این دو صندوق نامناسب ارزیابی می‌شود. ارزش مسکن در مقایسه با آن‌ها عملکرد بهتری داشته و بازده نهایی آن از معیار مسکن بالاتر بوده است؛ با این حال، همراهی ماهانه ضعیف آن با مسکن اجازه نمی‌دهد آن را جانشین قابل اتکای سرمایه‌گذاری مستقیم در مسکن بدانیم.",
             "همه صندوق‌های اصلی از رشد دلار و شاخص کل بورس عقب مانده‌اند. ارتباط با دلار ضعیف و وابسته به فاصله زمانی بررسی بوده است. رابطه مثبت با بورس، به‌ویژه برای کلید، وجود دارد؛ بنابراین مسئله اصلی، نبود هرگونه ارتباط با بازارها نیست، بلکه تحویل‌ندادن مواجهه ملکی مورد انتظار و عملکرد ضعیف نسبت به معیارهای مقایسه است.",
             "ترکیب دارایی نیز با تصویر یک سرمایه‌گذاری تماماً ملکی فاصله دارد. این تفاوت در دانیک برجسته است: در بخش‌هایی از دوره، بخش عمده دارایی صندوق غیرملکی بوده است. در ارزش مسکن، سهم ملک بالاتر بوده، اما آن هم در طول دوره کاهش یافته است. این شواهد، بررسی تصمیم‌های تخصیص دارایی و کیفیت اجرای هدف صندوق را ضروری می‌کند؛ تعیین سهم دقیق مدیریت در نتیجه، به تفکیک اثر ترکیب دارایی، عملکرد املاک و تغییر فاصله قیمت واحدها از ارزش خالص دارایی‌ها نیاز دارد.",
             r"\section{دامنه و مبنای ارزیابی}",
             "بازده صندوق‌ها بر اساس قیمت معامله‌شده و سرمایه‌گذاری مجدد سودهای نقدی ثبت‌شده محاسبه شده است. مطابق تأیید ارائه‌کننده اطلاعات، تاریخ پرداخت‌ها از صورت‌های مالی احراز شده است. فرض محاسباتی پروژه، خرید مجدد واحدها در نخستین روز معاملاتی از تاریخ مجمع است؛ این فرض با تاریخ واقعی واریز وجه یک مفهوم نیست. گزارش از همین روش مصوب پروژه استفاده می‌کند.",
             "مقایسه بازارها عمدتاً دوساله است. برای مسکن از قیمت پیشنهادی مسکن تهران در داده‌های کیلید استفاده شده و درآمد اجاره در آن منظور نشده است. تاریخ ابتدا و انتهای سری ماهانه مسکن اندکی با سری هفتگی بازارها تفاوت دارد؛ بنابراین فاصله بازده با مسکن مقایسه‌ای تقریبی در یک دوره نزدیک است. در بخش ترکیب دارایی، ارزش مسکن و دانیک بررسی می‌شوند. کاخ در جداول همبستگی کوتاه‌مدت حضور دارد، اما وارد رتبه‌بندی بازده دوساله نمی‌شود.",
             r"\section{بازده سرمایه‌گذار و فاصله از بازارهای مرجع}"]
    rows = []
    for asset in (*FUNDS, "TEDPIX", "USD/IRR"):
        s = summary.loc[asset]
        rows.append([NAMES[asset], p(s.cumulative_return), jalali(s.baseline_week_end), jalali(s.latest_observed_week_end)])
    rows.append(["مسکن تهران", p(housing.cumulative_return), jalali(housing.baseline_observation_date), jalali(housing.latest_observation_date)])
    parts += [table(["دارایی", "بازده تجمعی", "ابتدای دوره", "انتهای دوره"], rows)]
    rows = []
    for fund, name in FUNDS.items():
        r = summary.loc[fund, "cumulative_return"]
        rows.append([name, number(100*(r-housing.cumulative_return), signed=True),
                     number(100*(r-summary.loc['TEDPIX','cumulative_return']), signed=True),
                     p((1+r)/(1+summary.loc['USD/IRR','cumulative_return'])-1)])
    parts += ["در جدول بعد، فاصله با مسکن و بورس بر حسب واحد درصد است. ستون آخر کاهش یا افزایش ارزش ثروت نهایی نسبت به نگهداری دلار را نشان می‌دهد و با تفاضل ساده بازده‌ها تفاوت دارد.",
              table(["صندوق", "فاصله با مسکن", "فاصله با بورس", "تغییر قدرت خرید دلاری"], rows),
               "بازده مثبت ریالی به معنای حفظ قدرت خرید سرمایه‌گذار نیست. کلید و دانیک در این دوره هم نسبت به مسکن و هم نسبت به دلار و بورس عقب مانده‌اند. ارزش مسکن از نظر بازده نهایی از معیار مسکن بالاتر بوده، اما در مقایسه با دلار و بورس عقب‌ماندگی بزرگی دارد. بنابراین برتری آن نسبت به معیار مسکن به معنای برتری بر همه گزینه‌های مقایسه‌شده نیست.",
              r"\subsection{افت ارزش در طول مسیر}"]
    rows = []
    for fund, name in FUNDS.items():
        values = panel.loc[panel.asset.eq(fund)].sort_values("week_end_gregorian").cumulative_return.dropna()+1
        rows.append([name, p((values/values.cummax()-1).min())])
    parts += [table(["صندوق", "بیشترین افت از قله هفتگی"], rows),
              "این ارقام افت از بیشترین ارزش قبلی را در نقاط هفتگی نشان می‌دهد. بازده پایان دوره، شدت زیان موقتی در مسیر را پنهان می‌کند؛ افت بین نقاط ثبت‌شده نیز ممکن است بیشتر بوده باشد.",
              r"\section{سود نقدی و اثر خرید مجدد واحدها}",
              "رویدادهای زیر در محاسبه بازده اعمال شده‌اند. ستون خرید مجدد به زمان اجرای فرض محاسباتی اشاره دارد، نه تاریخ واریز سود. سود هر واحد به ریال بیان شده است.",
              table(["صندوق", "تاریخ مجمع", "خرید مجدد", "سود هر واحد"],
                    [[NAMES[r.fund], jalali(r.assembly_date_gregorian), jalali(r.reinvestment_date_gregorian), number(r.cash_irr_per_unit,0)] for r in events.itertuples()])]
    rows = []
    for fund in ("Kelid", "Danik"):
        s = daily.loc[daily.fund.eq(fund)].sort_values("source_date_gregorian")
        a = s.traded_close_irr.iloc[-1]/s.traded_close_irr.iloc[0]-1
        b = s.reinvested_value_irr.iloc[-1]/s.reinvested_value_irr.iloc[0]-1
        rows.append([NAMES[fund], p(a), p(b), number(100*(b-a))])
    parts += ["مقایسه زیر از نخستین معامله هر صندوق تا آخرین معامله موجود محاسبه شده است؛ بنابراین دوره آن با جدول دوساله یکسان نیست و برای رتبه‌بندی مشترک صندوق‌ها به کار نمی‌رود.",
              table(["صندوق", "رشد قیمت واحد", "بازده با خرید مجدد سود", "تفاوت به واحد درصد"], rows),
              r"\section{همراهی با مسکن و بازار سهام}",
               "دو معیار باید جدا بررسی شوند: میزان رشد نهایی سرمایه و همراهی تغییرات بازده در طول زمان. ارزش مسکن در پایان دوره از معیار مسکن جلوتر بوده، اما ماه‌به‌ماه آن را دنبال نکرده است. همبستگی نزدیک صفر نشان‌دهنده همراهی اندک و مقدار منفی نشان‌دهنده حرکت خلاف‌جهت است؛ هیچ‌یک به‌تنهایی اندازه فاصله بازده تجمعی را مشخص نمی‌کند.",
              "در افق دوساله، همبستگی ماهانه کلید با شاخص کل بورس از ارزش مسکن و دانیک بیشتر است. هر سه رابطه مثبت دارند، در حالی که همبستگی آن‌ها با مسکن نزدیک صفر یا منفی است. نتیجه در مورد مواجهه ملکی روشن است: قیمت واحدهای این صندوق‌ها در دوره بررسی‌شده رفتار بازار مسکن را به‌خوبی بازتاب نداده است.",
              r"\section{رابطه با دلار و اهمیت فاصله زمانی}",
              "در سه ماه اخیر، رابطه روزانه هر سه صندوق با دلار منفی و نسبتاً ضعیف است. در بررسی دوساله نیز همبستگی بازده هفتگی با تغییرات دلار در حدود یک، سه و شش ماه قبل، ضعیف و منفی است. از این نتایج نمی‌توان انتظار داشت جهش دلار با فاصله‌ای مشخص و قابل اتکا به رشد قیمت واحدهای صندوق تبدیل شود.",
              "بررسی جداگانه فاصله‌های یک و دو هفته‌ای، با درنظرگرفتن رفتار قبلی صندوق و بورس، نشانه‌هایی از رابطه مثبت نشان می‌دهد. با این حال، سهم توضیح‌داده‌شده از تغییرات بازده محدود است. این یافته با همبستگی ضعیف در فاصله‌های یک تا شش‌ماهه تعارض ندارد؛ فاصله زمانی و نحوه مقایسه متفاوت است.",
              r"\section{ترکیب دارایی ارزش مسکن و دانیک}"]
    rows = []
    for fund in ("Arzesh Maskan", "Danik"):
        s = mix.loc[mix.fund.eq(fund)].sort_values("jalali_period")
        a,b = s.iloc[0],s.iloc[-1]
        rows.append([NAMES[fund],p(a.housing_share),p(b.housing_share),p(s.housing_share.mean()),p(s.housing_share.min()),p(b.fixed_income_share)])
        parts.append(r"\textbf{"+NAMES[fund]+".} سهم ملک از "+p(a.housing_share)+" به "+p(b.housing_share)
                     +" رسیده و میانگین آن در دوره "+p(s.housing_share.mean())+" بوده است. کمترین سهم ملک "
                     +p(s.housing_share.min())+" و بیشترین سهم درآمد ثابت "+p(s.fixed_income_share.max())
                     +" است. در پایان دوره، "+p(1-b.housing_share)+" از دارایی‌ها غیرملکی بوده؛ سهم درآمد ثابت "
                     +p(b.fixed_income_share)+" و سهم سایر دارایی‌ها "+p(b.other_including_cash_equity_share)+" است.")
    parts += [table(["صندوق","ملک ابتدا","ملک پایان","میانگین ملک","کمترین ملک","درآمد ثابت پایان"],rows),
              "در دانیک، میانگین پایین سهم ملک و غلبه درآمد ثابت در بخشی از دوره نشان می‌دهد سرمایه‌گذار عملاً همواره مواجهه غالب با ملک دریافت نکرده است. این نکته با انتظاری که صرفاً از عنوان صندوق املاک ایجاد می‌شود فاصله دارد. در ارزش مسکن، مواجهه ملکی بیشتر بوده، اما سهم غیرملکی نیز قابل توجه و رو به افزایش بوده است.",
              "«سایر» شامل وجه نقد، سهام و سایر دارایی‌ها و مطالبات است. در پایان دوره، بخش عمده این سرفصل در دانیک مربوط به سایر دارایی‌ها و مطالبات است و نباید آن را تماماً نقد یا درآمد ثابت تلقی کرد. سهم‌های گزارش‌شده ترکیب حسابداری دارایی‌ها هستند و به‌تنهایی سهم هر جزء از بازده صندوق را نشان نمی‌دهند.",
              r"\section{ارزیابی نهایی و اولویت بررسی مدیریتی}",
              "برای هدف مشخص دنبال‌کردن رشد قیمت مسکن، کلید و دانیک در دوره بررسی‌شده گزینه‌های مناسبی نبوده‌اند: بازده آن‌ها پایین‌تر از معیار مسکن بوده و همراهی بازده ماهانه نیز ضعیف است. ارزش مسکن در رتبه بهتری قرار دارد، اما برتری آن نسبت به دو صندوق دیگر، تضمین‌کننده مواجهه قابل اتکا با مسکن نیست. این قضاوت درباره کارنامه دوره بررسی است، نه پیش‌بینی قطعی عملکرد آینده.",
              "اولویت بررسی مدیریتی، توضیح فاصله میان هدف سرمایه‌گذاری ملکی و نتیجه‌ای است که به دارنده واحد رسیده است. تصمیم‌های تخصیص به درآمد ثابت و مطالبات، عملکرد عملیاتی املاک، هزینه‌های صندوق و تغییر فاصله قیمت تابلو با ارزش خالص دارایی‌ها باید جداگانه ارزیابی شوند. وجود دارایی غیرملکی و عملکرد ضعیف، شواهدی برای طرح این پرسش‌هاست؛ اما تعیین سهم هر عامل از عقب‌ماندگی بدون تفکیک بازده اجزا ممکن نیست.",
              r"\section{جداول کامل همبستگی}",
              "ستون‌ها افق زمانی بررسی را نشان می‌دهند. مسکن فقط ماهانه بررسی شده است. خط تیره به معنی نتیجه قابل گزارش نبودن آن خانه است. برای خوانایی، تعداد مشاهدات و جزئیات آزمون‌ها در این گزارش درج نشده‌اند."]
    titles = ["بورس ـ بازده روزانه", "بورس ـ بازده هفتگی", "بورس ـ بازده ماهانه", "مسکن ـ بازده ماهانه", "دلار ـ بازده روزانه", "دلار با تقدم زمانی ـ بازده هفتگی در دوره دوساله"]
    for title,spec in zip(titles,GRID_SPECS):
        benchmark,frequency,xs,field,_,_ = spec
        s = grid.loc[grid.benchmark.eq(benchmark)&grid.frequency.eq(frequency)]
        rows=[]
        for fund,name in {**FUNDS,"Kakh":"کاخ"}.items():
            row=[name]
            for x in xs:
                cell=s.loc[s.fund.eq(fund)&s[field].eq(x)].iloc[0]
                row.append("—" if pd.isna(cell.correlation) else signed(cell.correlation))
            rows.append(row)
        headers=["صندوق"]+[digits(x)+(" هفته قبل" if field=="lag_weeks" else " ماه") for x in xs]
        parts += [r"\subsection*{"+title+"}",table(headers,rows)]
    parts += ["در جدول تقدم زمانی دلار، چهار، سیزده و بیست‌وشش هفته تقریباً معادل یک، سه و شش ماه است. نتایج کوتاه‌مدت ممکن است تغییر کنند و نباید صرفاً یک افق مطلوب برای قضاوت انتخاب شود.",
              r"\section{نتیجه بررسی تکمیلی دلار در فاصله یک و دو هفته}",
              "جدول زیر نشان می‌دهد مدل بررسی‌شده چه سهمی از تغییرات بازده هفتگی را توضیح داده و افزودن اطلاعات قبلی دلار چقدر این سهم را افزایش داده است. افزایش توضیح‌دهندگی با تضمین توان پیش‌بینی آینده برابر نیست.",
              table(["صندوق","سهم توضیح‌داده‌شده","افزایش با افزودن دلار"],
                    [[NAMES[r.fund],p(r.r_squared),number(100*r.incremental_r_squared)+" واحد درصد"]
                     for r in models.itertuples() if r.status=="reported"]),
              r"\section{پیوست ترکیب ماهانه دارایی‌ها}",
              "همه ارقام سهم از کل دارایی‌ها هستند. دوره مهر ۱۴۰۳ تا شهریور ۱۴۰۵ را پوشش می‌دهند. میانگین‌های متن، میانگین ساده همین مقاطع ماهانه است."]
    for fund in ("Arzesh Maskan","Danik"):
        s=mix.loc[mix.fund.eq(fund)].sort_values("jalali_period")
        parts += [r"\subsection*{"+NAMES[fund]+"}",longtable(["ماه","ملک","درآمد ثابت","سایر"],
                    [[digits(r.jalali_period),p(r.housing_share),p(r.fixed_income_share),p(r.other_including_cash_equity_share)] for r in s.itertuples()])]
    parts += [r"\section{پیوست بازده ماهانه صندوق‌ها}",
              "بازده ماهانه با لحاظ سرمایه‌گذاری مجدد سودهای ثبت‌شده گزارش شده است؛ خانه خالی با خط تیره نمایش داده می‌شود و به معنی بازده صفر نیست."]
    monthly=read("reit_reinvested_monthly_returns.csv")
    wide=monthly.loc[monthly.period.ge("1403/07")].pivot(index="period",columns="fund",values="reinvested_return").reindex(columns=FUNDS)
    parts += [longtable(["ماه",*FUNDS.values()],[[digits(period),*("—" if pd.isna(v) else p(v) for v in row)] for period,row in wide.iterrows()]),
              r"\section{یادداشت منابع}",
              "منابع گزارش، خروجی‌های فعال پروژه برای قیمت صندوق‌ها، شاخص کل بورس، دلار، مسکن تهران و فایل ترکیب دارایی گردآوری‌شده از کدال است. بخشی از تفکیک دارایی‌ها در فایل کدال بازسازی شده است: برای ارزش مسکن در شهریور ۱۴۰۴ اختلاف جمع اجزای دارایی ثبت شده و برای دانیک در آذر و دی ۱۴۰۴ سهم ملک با سقف سرفصل حسابداری تطبیق داده شده است. این موارد در داده نگهداری شده‌اند و ارقام به‌عنوان ترکیب گزارش‌شده و بازسازی‌شده تفسیر می‌شوند. این نسخه از داده‌های موجود استفاده می‌کند و به معنای دریافت اطلاعات جدید از منابع نیست.",
              r"\end{document}"]
    REPORT.write_text("\n\n".join(parts)+"\n",encoding="utf-8")
    return REPORT


if __name__=="__main__":
    print(build())
