"""Real-time P-wave detection via a recursive STA/LTA characteristic function.
The (trigger_on, trigger_off) interface matches a learned picker drop-in."""
import numpy as np
from obspy import read
from obspy.signal.trigger import recursive_sta_lta, trigger_onset

st = read("marmara_event.mseed").select(channel="HHZ")
picks = {}
for tr in st:
    df = tr.stats.sampling_rate
    cft = recursive_sta_lta(tr.data, int(1.0 * df), int(10.0 * df))
    onsets = trigger_onset(cft, thr_on=3.5, thr_off=1.5)
    if len(onsets):                     # first onset -> P arrival
        p_sample = onsets[0][0]
        picks[tr.id] = tr.stats.starttime + p_sample / df
for tid, tp in sorted(picks.items()):
    print(f"{tid}: P at {tp.isoformat()}")
np.save("p_picks.npy", picks, allow_pickle=True)
