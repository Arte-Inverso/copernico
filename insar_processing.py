import os
import subprocess
import time

# Discovery Configuration
SNAP_BIN = r"C:\Program Files\esa-snap\bin"
GPT_PATH = os.path.join(SNAP_BIN, "gpt.exe")
DATA_DIR = r"c:\Copernico"
MASTER = os.path.join(DATA_DIR, "S1A_IW_SLC__1SDV_20260310T105208_20260310T105236_063564_07FCFB_FA9C.SAFE")
SLAVE = os.path.join(DATA_DIR, "S1C_IW_SLC__1SDV_20260316T105045_20260316T105113_006788_00DB83_BEA4.SAFE")

OUTPUT_DIM = os.path.join(DATA_DIR, "purace_slant_range_discovery.dim")
GRAPH_FILE = os.path.join(DATA_DIR, "insar_discovery.xml")

graph_xml = f"""<graph id="InSAR_Discovery">
  <version>1.0</version>
  <node id="Read-Master"><operator>Read</operator><parameters><file>{MASTER}</file></parameters></node>
  <node id="Read-Slave"><operator>Read</operator><parameters><file>{SLAVE}</file></parameters></node>

  <node id="Split-Master"><operator>TOPSAR-Split</operator>
    <sources><sourceProduct refid="Read-Master"/></sources>
    <parameters><subswath>IW1</subswath><selectedPolarisations>VV</selectedPolarisations><firstBurstIndex>1</firstBurstIndex><lastBurstIndex>2</lastBurstIndex></parameters>
  </node>
  <node id="Split-Slave"><operator>TOPSAR-Split</operator>
    <sources><sourceProduct refid="Read-Slave"/></sources>
    <parameters><subswath>IW1</subswath><selectedPolarisations>VV</selectedPolarisations><firstBurstIndex>8</firstBurstIndex><lastBurstIndex>9</lastBurstIndex></parameters>
  </node>

  <node id="Orbit-Master"><operator>Apply-Orbit-File</operator>
    <sources><sourceProduct refid="Split-Master"/></sources>
    <parameters><orbitType>Sentinel Restituted (Auto Download)</orbitType><continueOnFail>true</continueOnFail></parameters>
  </node>
  <node id="Orbit-Slave"><operator>Apply-Orbit-File</operator>
    <sources><sourceProduct refid="Split-Slave"/></sources>
    <parameters><orbitType>Sentinel Restituted (Auto Download)</orbitType><continueOnFail>true</continueOnFail></parameters>
  </node>

  <node id="Back-Geocoding"><operator>Back-Geocoding</operator>
    <sources><sourceProduct refid="Orbit-Master"/><sourceProduct.1 refid="Orbit-Slave"/></sources>
    <parameters><demName>SRTM 3Sec</demName></parameters>
  </node>

  <node id="Interferogram"><operator>Interferogram</operator>
    <sources><sourceProduct refid="Back-Geocoding"/></sources>
  </node>

  <node id="Deburst"><operator>TOPSAR-Deburst</operator>
    <sources><sourceProduct refid="Interferogram"/></sources>
  </node>

  <node id="TopoPhaseRemoval"><operator>TopoPhaseRemoval</operator>
    <sources><sourceProduct refid="Deburst"/></sources>
    <parameters><demName>SRTM 3Sec</demName></parameters>
  </node>

  <node id="Write">
    <operator>Write</operator>
    <sources><sourceProduct refid="TopoPhaseRemoval"/></sources>
    <parameters>
      <file>{OUTPUT_DIM}</file>
      <formatName>BEAM-DIMAP</formatName>
    </parameters>
  </node>
</graph>
"""

def run():
    print("Running Stage 1 Discovery (TopoPhaseRemoval -> Write)...")
    with open(GRAPH_FILE, 'w') as f: f.write(graph_xml)
    subprocess.run([GPT_PATH, GRAPH_FILE])

if __name__ == "__main__":
    run()
