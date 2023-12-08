select * 
from core_wip.timeseries_{{ freq }}
join core_wip.timeseries_lookup
using (series_id)