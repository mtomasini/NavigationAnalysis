# Analysis of performance data of reconstructed proto-historic boats

> Authors: Boel K. Bengtsson, Björn Bengtsson, Alvaro Montenegro, **Matteo Tomasini**
>
> Date: 28.09.2023

In this repository, I analyse the data collected during various sessions of navigation in Brittany, France. During the sessions, different tests were performed, from towing tests to measure the drag resistance of the hull of different vessels in the water, to navigation trials (A-B straight line navigation).

The data was collected and produced through the Actisense / EBL tooling and software, then transformed into CSV files and finally analysed. For the moment being, the data won't be uploaded to this repository. CSV files are further analysed in Python using `pandas`.

## Tasks / planning of work

Expected pipeline:

1) Download data in csv for:

    - Vessel Heading
    - Speed, Water Referenced
    - Position, Rapid Update
    - Wind Data

    1bis) In a second time we could add COG & SOG (Course Over Ground and Speed Over Ground) as well as GNSS Position Data

2) Bin data together by 1s (or 5s ?), where necessary
3) Plot:

    - course on map (interactive? How do we select points of departure and arrival?)
    - Plot winds on same map
    - Plot avg speed on selected transect
    - Plot avg direction on selected transect
