# BTC Map data

Bitcoin location data is pulled from [OpenStreetMap](https://www.openstreetmap.org) every 10 minutes.

## Contributing

[New locations ready for Shadowy Supertaggers](https://github.com/teambtcmap/btcmap-data/issues?q=is%3Aissue+is%3Aopen+sort%3Acreated-asc+label%3Alocation-submission+-label%3Aassigned+no%3Aassignee) 🆕

[Verified locations ready for Shadowy Supertaggers](https://github.com/teambtcmap/btcmap-data/issues?q=is%3Aopen+is%3Aissue+label%3A%22verify-submission%22+-label%3Aassigned+no%3Aassignee) �

All location submissions from [btcmap.org/add-location](https://btcmap.org/add-location) that still need to be added to [OpenStreetMap](http://openstreetmap.com) (if valid) have an open issue in this repository with the label `location-submission`. Locations that have had a verified submission from [btcmap.org/verify-location](https://btcmap.org/verify-location) will have a `verify-submission` label. These need to have their `survey:date`, `check_date` or `check_date:currency:XBT` tag and any other additional information updated on OSM.

You can filter the issues by these labels (see links above for issues that have yet to be assigned).

Anyone can participate, you can check out the [Wiki](https://github.com/teambtcmap/btcmap-general/wiki/Tagging-Merchants) for more details on how to add/edit locations to OpenStreetMap and become a Shadowy Supertagger 🥷.

Thanks for your contribution to the bitcoin mapping community!

## Be notified of new submissions

- You can be notified of new submissions by setting `Watch` on this repo to `Custom` > `Issues`.

- You can follow the [BTC Map Noob Bot](https://github.com/BTCMap-NoobBot) account.

- You can join the [github-data](https://discord.gg/p8hj6SVx9X) Discord channel where the submissions are posted.

## Tagging stats

[BTC Map Dashboard](https://btcmap.org/dashboard)

`currency:XBT` https://taginfo.openstreetmap.org/keys/currency:XBT#chronology

`payment:onchain` https://taginfo.openstreetmap.org/keys/payment:onchain#chronology

`payment:lightning` https://taginfo.openstreetmap.org/keys/payment:lightning#chronology

`payment:lightning_contactless` https://taginfo.openstreetmap.org/keys/payment:lightning_contactless#chronology

---

![Untitled](https://user-images.githubusercontent.com/85003930/194117128-2f96bafd-2379-407a-a584-6c03396a42cc.png)


## Development

```bash
npm install || pip install -r requirements.txt
npm test || pytest
```
