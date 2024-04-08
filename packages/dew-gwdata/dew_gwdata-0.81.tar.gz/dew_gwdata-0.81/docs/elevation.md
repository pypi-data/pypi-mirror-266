```python
import dew_gwdata as gd
db = gd.sageodata()

wells = db.find_wells("ule205, sle69")
elevs = db.elevation_surveys(wells)
elevs.T
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
      <th>1</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>well_id</th>
      <td>ULE205</td>
      <td>SLE069</td>
    </tr>
    <tr>
      <th>dh_no</th>
      <td>198752</td>
      <td>198753</td>
    </tr>
    <tr>
      <th>unit_hyphen</th>
      <td>6028-2319</td>
      <td>6028-2320</td>
    </tr>
    <tr>
      <th>obs_no</th>
      <td>ULE205</td>
      <td>SLE069</td>
    </tr>
    <tr>
      <th>dh_name</th>
      <td>US 1</td>
      <td>REPLACEMENT FOR SLE010</td>
    </tr>
    <tr>
      <th>aquifer</th>
      <td>Tbw+Qpcb</td>
      <td>Tbw+Qpcb</td>
    </tr>
    <tr>
      <th>ref_point_type</th>
      <td>REF</td>
      <td>REF</td>
    </tr>
    <tr>
      <th>ref_elev</th>
      <td>67.717</td>
      <td>132.088</td>
    </tr>
    <tr>
      <th>elev_date</th>
      <td>2004-06-01 00:00:00</td>
      <td>2004-06-01 00:00:00</td>
    </tr>
    <tr>
      <th>ground_elev</th>
      <td>67.071</td>
      <td>131.644</td>
    </tr>
    <tr>
      <th>vert_accuracy</th>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>survey_meth</th>
      <td>GPSRD</td>
      <td>GPSRD</td>
    </tr>
    <tr>
      <th>applied_date</th>
      <td>2003-12-12 00:00:00</td>
      <td>2003-12-10 00:00:00</td>
    </tr>
    <tr>
      <th>ref_height</th>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>dist_elev_point_to_ground</th>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>comments</th>
      <td>sub 0.03m vertical and horizontal accuracy, ne...</td>
      <td>sub 0.03m vertical and horizontal accuracy, ne...</td>
    </tr>
    <tr>
      <th>created_by</th>
      <td>GASLE</td>
      <td>GASLE</td>
    </tr>
    <tr>
      <th>creation_date</th>
      <td>2004-07-23 13:04:04</td>
      <td>2004-07-23 10:07:00</td>
    </tr>
    <tr>
      <th>modified_by</th>
      <td>None</td>
      <td>GASLE</td>
    </tr>
    <tr>
      <th>modified_date</th>
      <td>NaT</td>
      <td>2004-07-23 10:07:39</td>
    </tr>
    <tr>
      <th>elev_no</th>
      <td>116050</td>
      <td>116033</td>
    </tr>
    <tr>
      <th>unit_long</th>
      <td>602802319</td>
      <td>602802320</td>
    </tr>
    <tr>
      <th>easting</th>
      <td>549935.34</td>
      <td>551461.01</td>
    </tr>
    <tr>
      <th>northing</th>
      <td>6147387.99</td>
      <td>6145300.55</td>
    </tr>
    <tr>
      <th>zone</th>
      <td>53</td>
      <td>53</td>
    </tr>
    <tr>
      <th>latitude</th>
      <td>-34.814536</td>
      <td>-34.833283</td>
    </tr>
    <tr>
      <th>longitude</th>
      <td>135.545995</td>
      <td>135.562804</td>
    </tr>
  </tbody>
</table>
</div>




```python
hs = db.hydrostrat_logs(wells)
hs = gd.depth_to_elev(hs)
hs[['obs_no', 'unit_depth_from', 'unit_depth_to', 'unit_depth_from_mahd', 'unit_depth_to_mahd']]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>obs_no</th>
      <th>unit_depth_from</th>
      <th>unit_depth_to</th>
      <th>unit_depth_from_mahd</th>
      <th>unit_depth_to_mahd</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ULE205</td>
      <td>0.0</td>
      <td>90.0</td>
      <td>64.371674</td>
      <td>-25.628326</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ULE205</td>
      <td>90.0</td>
      <td>NaN</td>
      <td>-25.628326</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>SLE069</td>
      <td>0.0</td>
      <td>152.0</td>
      <td>129.020493</td>
      <td>-22.979507</td>
    </tr>
    <tr>
      <th>3</th>
      <td>SLE069</td>
      <td>152.0</td>
      <td>NaN</td>
      <td>-22.979507</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python

```
