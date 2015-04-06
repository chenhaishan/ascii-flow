# Todo Items #

  * ~~fix pos\_in\_box\_b (it doesnt account for positions on the eastmost edge of a box)~~
  * line simplification
  * line arrows (parsing, rendering)
  * line serialization

# Broken Examples #

  * 
```
+---+
|   |
| +-+
| +-+
|   |
+---+
```

  * 
```
+---+
|   |
|   +--+
+---+
```

  * 
```
      +-+
+-+---+ | +---+
| |   | +-+-+-+
| |   | |   +-+
| +-+ | ++  | |
+---+-+-++--+-+
```