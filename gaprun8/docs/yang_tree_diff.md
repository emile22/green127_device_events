# YANG Tree Diff

```diff
--- yang_tree_before.txt
+++ yang_tree_after.txt
@@ -98,3 +98,14 @@
               +--rw oper?    -> /energy-objects/energy-object/power-state/oper
 
 ## ietf-yang-types@2013-07-15.yang
+
+
+
+## example-green-power-energy-gaps.yang
+
+module: example-green-power-energy-gaps
+
+  augment /eo:energy-objects/eo:energy-object:
+    +--ro battery-state-of-charge
+       +--ro status                     enumeration
+       +--ro state-of-charge-percent    decimal64
```
