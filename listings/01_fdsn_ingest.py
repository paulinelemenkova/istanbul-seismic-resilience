"""Ingest open seismic waveforms for the Marmara region from an FDSN service
(KOERI or AFAD) and stage them for the Istanbul digital twin."""
from obspy import UTCDateTime
from obspy.clients.fdsn import Client

client = Client("KOERI")               # AFAD / IRIS also expose FDSN endpoints
t0 = UTCDateTime("2019-09-26T10:59:25")  # example Silivri Mw 5.8 origin time

st = client.get_waveforms(
    network="KO", station="*", location="*", channel="HH?",
    starttime=t0 - 10, endtime=t0 + 120,
    latitude=40.88, longitude=28.20, maxradius=1.5)  # ~ Marmara aperture

st.merge(method=1).detrend("demean").taper(0.05)
st.filter("bandpass", freqmin=0.5, freqmax=20.0, corners=4, zerophase=True)
st.write("marmara_event.mseed", format="MSEED")
print(f"Fetched {len(st)} traces from {len({tr.stats.station for tr in st})} stations")
