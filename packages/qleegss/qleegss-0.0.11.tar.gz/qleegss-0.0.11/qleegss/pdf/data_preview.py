import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table, TableStyle, Image


def generate_data_preview(data):
    eeg_path = data.eeg_path
    fig_path = eeg_path.replace('eeg.eeg', 'data_preview.png')
    pdf_path = eeg_path.replace('eeg.eeg', 'sleep_report.pdf')
    record_date = data.start_time.strftime('%Y-%m-%d')

    start_time = data.start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time = data.end_time.strftime('%Y-%m-%d %H:%M:%S')

    content = {
        "sleep_plot": fig_path,
        "name": data.name,
        "phone_number": data.phone,
        "record_date": record_date,
        "record_start_time": start_time,
        "record_end_time": end_time,
        "disconnection_rate": "{:.2f}%".format(data.disconnect_rate),
        "package_loss_rate": "{:.2f}%".format(data.package_loss_rate),
        "header_mac": data.header_mac,
        "box_mac": data.box_mac,
    }

    pdf_plot(pdf_path, content)


def pdf_plot(pdf_save_path, Results):
    """
    生成分析报告
    :param pdf_save_path: PDF文件保存路径
    :param Results: 结果集
    :return:
    """
    base_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(base_path)
    font_path = os.path.join(dir_path, "msyhbd.ttc")
    pdfmetrics.registerFont(TTFont("Yahei", font_path))

    pdf_file = Canvas(pdf_save_path, pagesize=A4)

    TFimg = Image(Results["sleep_plot"], width=495, height=420) if Results["sleep_plot"] is not None else Image(width=495, height=420)

    Description = "备注：\n" \
                  "断连率：因记录子与接收器距离太远导致数据无法记录的时间占总记录时间的比例，断连率大于5%可能对分析结果造成明显影响。\n" \
                  "丢包率：因障碍物阻挡导致通信质量较差时导致的丢包。正常情况下，丢包率小于0.5%，丢包率大于5%可能对分析结果造成明显影响。"

    name = Results.get("name") if Results.get("name") is not None else "--"
    phone_number = Results.get("phone_number") if Results.get("phone_number") is not None else "--"
    record_date = Results.get("record_date") if Results.get("record_date") is not None else "--"
    record_start_time = Results.get("record_start_time") if Results.get("record_start_time") is not None else "--"
    record_end_time = Results.get("record_end_time") if Results.get("record_end_time") is not None else "--"
    package_loss_rate = Results.get("package_loss_rate") if Results.get("package_loss_rate") is not None else "--"
    disconnection_rate = Results.get("disconnection_rate") if Results.get("disconnection_rate") is not None else "--"
    sl = Results.get("sl") if Results.get("sl") is not None else None
    if sl is not None:
        sl = "{:.2f}".format(sl) if sl > 0 else "--"

    header_mac = Results.get("header_mac") if Results.get("header_mac") is not None else "--"
    box_mac = Results.get("box_mac") if Results.get("box_mac") is not None else "--"

    data = [
        ["数据预览"],
        ["姓名", name, "手机号", phone_number, "监测日期", record_date],

        ["记录子MAC", header_mac, '', "接收器MAC", box_mac],

        ["记录时间"],
        ["记录开始时间", record_start_time, "", "记录结束时间", record_end_time],
        ["信号质量"],
        ["断连率(%)", disconnection_rate, "", "丢包率(%)", package_loss_rate],
        ["数据预览图"],
        [TFimg],
        [Description],
        [""]
    ]
    SPAN_SPAN_SPAN_SPAN_ = [("SPAN", (0, 0), (-1, 0)),
                            ("SPAN", (0, 3), (-1, 3)),
                            ("SPAN", (0, 5), (-1, 5)),

                            ("SPAN", (0, 7), (-1, 7)),
                            ("SPAN", (0, 8), (-1, 8)),
                            ("SPAN", (0, 9), (-1, 9)),

                            ("SPAN", (1, 2), (2, 2)),
                            ("SPAN", (4, 2), (5, 2)),

                            ("SPAN", (1, 4), (2, 4)),
                            ("SPAN", (-2, 4), (-1, 4)),

                            ("SPAN", (1, 6), (2, 6)),
                            ("SPAN", (4, 6), (5, 6)),

                            ("SPAN", (0, -1), (-1, -1)),

                            ]
    merged_cells = SPAN_SPAN_SPAN_SPAN_

    table = Table(data, colWidths=[80, 100, 80, 100, 80, 100])
    table.setStyle(TableStyle([
        *merged_cells,
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-2, -3), "CENTER"),
        ("ALIGN", (-1, -2), (-1, -2), "TA_LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Yahei"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("GRID", (0, 0), (-1, -2), 1, colors.black),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 100),
    ]))

    table.wrapOn(pdf_file, 0, 0)
    table.drawOn(pdf_file, 28, 10)

    pdf_file.save()
