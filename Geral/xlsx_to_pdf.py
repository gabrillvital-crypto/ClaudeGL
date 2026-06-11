import win32com.client
import os

XLSX = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Oportunidades_Dock_Brasil.xlsx"
PDF  = r"C:\Users\gabriel.evangelista\Documents\ClaudeGL\Oportunidades_Dock_Brasil.pdf"

excel = win32com.client.Dispatch("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

wb = excel.Workbooks.Open(XLSX)

sheet_configs = {
    "Oportunidades de Automação":  {"cols": "F", "orient": 2},  # landscape
    "Para Desenvolvimento":         {"cols": "F", "orient": 2},
}

for i in range(1, wb.Worksheets.Count + 1):
    ws = wb.Worksheets(i)
    name = ws.Name
    cfg  = sheet_configs.get(name, {"cols": "F", "orient": 2})

    last_row = ws.UsedRange.Row + ws.UsedRange.Rows.Count - 1
    ws.PageSetup.PrintArea     = f"$A$1:${cfg['cols']}${last_row}"
    ws.PageSetup.Orientation   = cfg["orient"]
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.FitToPagesTall = False
    ws.PageSetup.Zoom           = False
    ws.PageSetup.PaperSize      = 9      # A4
    ws.PageSetup.TopMargin      = excel.InchesToPoints(0.35)
    ws.PageSetup.BottomMargin   = excel.InchesToPoints(0.35)
    ws.PageSetup.LeftMargin     = excel.InchesToPoints(0.35)
    ws.PageSetup.RightMargin    = excel.InchesToPoints(0.35)
    ws.PageSetup.PrintTitleRows = "$1:$4"

    print(f"  {name}: área A1:{cfg['cols']}{last_row}, {'paisagem' if cfg['orient']==2 else 'retrato'}")

wb.ExportAsFixedFormat(0, PDF)
wb.Close(False)
excel.Quit()

print(f"\nPDF gerado: {PDF}")
print(f"Tamanho: {os.path.getsize(PDF):,} bytes")
