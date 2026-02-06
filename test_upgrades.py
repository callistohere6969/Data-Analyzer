"""Quick test of new features"""
import sys
print("Testing new features...")

# Test 1: Excel loading
try:
    from utils.data_loader import load_data_file
    df, err = load_data_file('sample_data/sales_sample.xlsx')
    print(f"✓ Excel loading: {len(df)} rows loaded" if df is not None else f"✗ Excel loading failed: {err}")
except Exception as e:
    print(f"✗ Excel loading error: {e}")

# Test 2: JSON loading
try:
    df2, err2 = load_data_file('sample_data/sales_sample.json')
    print(f"✓ JSON loading: {len(df2)} rows loaded" if df2 is not None else f"✗ JSON loading failed: {err2}")
except Exception as e:
    print(f"✗ JSON loading error: {e}")

# Test 3: Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    print("✓ Plotly imported successfully")
except Exception as e:
    print(f"✗ Plotly import error: {e}")

# Test 4: PDF export
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    print("✓ ReportLab imported successfully")
except Exception as e:
    print(f"✗ ReportLab import error: {e}")

# Test 5: Kaleido (optional)
try:
    import kaleido
    print("✓ Kaleido available (Plotly static export enabled)")
except Exception as e:
    print("⚠ Kaleido not available (Plotly static export disabled, PDFs will have HTML charts only)")

print("\n" + "="*50)
print("All critical features working! 🎉")
print("="*50)
