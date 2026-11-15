import os
import subprocess
import time

# Paths
GPT_PATH = r"C:\Program Files\esa-snap\bin\gpt.exe"
DATA_DIR = r"c:\Copernico"
INPUT_DIM = os.path.join(DATA_DIR, "purace_slant_range_discovery.dim")
OUTPUT_TC = os.path.join(DATA_DIR, "purace_insar_tc_final.dim")
GRAPH_FILE = os.path.join(DATA_DIR, "insar_tc_v8.xml")

# Updated XML with explicit FLOAT32 for both Phase and Coherence
xml_graph = f"""<graph id="InSAR_TC">
  <version>1.0</version>
  <node id="Read">
    <operator>Read</operator>
    <parameters>
      <file>{INPUT_DIM}</file>
    </parameters>
  </node>

  <node id="BandMaths">
    <operator>BandMaths</operator>
    <sources><sourceProduct refid="Read"/></sources>
    <parameters>
      <targetBands>
        <targetBand>
          <name>phase_ifg</name>
          <expression>atan2(q_ifg_VV_10Mar2026_16Mar2026, i_ifg_VV_10Mar2026_16Mar2026)</expression>
          <type>float32</type>
        </targetBand>
        <targetBand>
          <name>coh_ifg</name>
          <expression>coh_IW1_VV_10Mar2026_16Mar2026</expression>
          <type>float32</type>
        </targetBand>
      </targetBands>
    </parameters>
  </node>

  <node id="TerrainCorrection">
    <operator>Terrain-Correction</operator>
    <sources>
      <sourceProduct refid="BandMaths"/>
    </sources>
    <parameters>
      <sourceBands>phase_ifg,coh_ifg</sourceBands>
      <demName>SRTM 1Sec HGT</demName>
      <demResamplingMethod>BILINEAR_INTERPOLATION</demResamplingMethod>
      <imgResamplingMethod>BILINEAR_INTERPOLATION</imgResamplingMethod>
      <pixelSpacingInMeter>20.0</pixelSpacingInMeter>
      <mapProjection>WGS84(DD)</mapProjection>
      <alignToStandardGrid>false</alignToStandardGrid>
      <saveSelectedSourceBand>true</saveSelectedSourceBand>
    </parameters>
  </node>

  <node id="Write">
    <operator>Write</operator>
    <sources>
      <sourceProduct refid="TerrainCorrection"/>
    </sources>
    <parameters>
      <file>{OUTPUT_TC}</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
</graph>
"""

def run_tc():
    print("Starting Final Corrected InSAR Geocoding (Stage 2: Float32 Phase + Coherence)...")
    if not os.path.exists(INPUT_DIM):
        print(f"ERROR: {INPUT_DIM} not found.")
        return

    # Cleanup stale
    if os.path.exists(OUTPUT_TC): os.remove(OUTPUT_TC)
    tc_data = OUTPUT_TC.replace('.dim', '.data')
    if os.path.exists(tc_data):
        import shutil
        shutil.rmtree(tc_data, ignore_errors=True)

    with open(GRAPH_FILE, 'w') as f:
        f.write(xml_graph)
    
    cmd = [GPT_PATH, GRAPH_FILE]
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        for line in process.stdout:
            print(line.strip())
        process.wait()
        if process.returncode == 0:
            print(f"Stage 2 SUCCESS: {OUTPUT_TC}")
        else:
            print(f"Stage 2 FAILED: {process.returncode}")
    except Exception as e:
        print(f"Error during Stage 2: {e}")

if __name__ == "__main__":
    run_tc()
