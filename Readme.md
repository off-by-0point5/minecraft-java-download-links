The python script included in this repository scrapes mcversions.net and produces those following two files.

In versions.json all versions are arranged in this way:

```json
{
  "stable": {
    "1.16.1": {
      "server": "https://launcher.mojang.com/v1/objects/.../server.jar",
      "client": "https://launcher.mojang.com/v1/objects/.../client.jar",
      "date": "2020-06-24"
    }
  },
  "snapshot": {...},
  "beta": {...},
  "alpha": {...}
}
```

In versions-list.json they are all in a single list. Less readable for a human but easier to search an sort with a program.

```json
[
  {
    "date": "2020-11-04",
    "type": "snapshot",
    "version": "20w45a",
    "server": "https://launcher.mojang.com/v1/objects/.../server.jar",
    "client": "https://launcher.mojang.com/v1/objects/.../client.jar"
  },
  {...}
]
```