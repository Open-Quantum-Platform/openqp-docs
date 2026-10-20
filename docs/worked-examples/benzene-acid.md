# Benzene: Ring Current and Aromaticity (ACID)

The anisotropy of the induced current density (ACID) shows where electrons are
delocalized when a magnetic field is applied. In a conjugated ring the ACID
isosurface forms a continuous belt around the ring, and the induced current
vectors show which way the ring current flows. A diatropic ring current is the
signature of aromaticity and causes the downfield shift of benzene protons in
NMR.

<div class="oqp-figs" markdown>
<figure markdown>
![ACID isosurface of benzene](../assets/worked-examples/acid-benzene.png)
<figcaption>ACID isosurface (0.05 a.u.): a continuous belt over the whole ring</figcaption>
</figure>
<figure markdown>
![Benzene](../assets/worked-examples/mol-benzene.png)
<figcaption>Benzene at the PBE0/6-31G* geometry</figcaption>
</figure>
</div>

## Copy and run

```text title="benzene-acid.oqp"
hf/6-31g* nmr(gauge=giao,acid=true)
geom="""
C      1.392883     0.000000     0.000000
C      0.696465     1.206259     0.000000
C     -0.696465     1.206259     0.000000
C     -1.392883     0.000000     0.000000
C     -0.696465    -1.206259     0.000000
C      0.696465    -1.206259     0.000000
H      2.479666     0.000000     0.000000
H      1.239913     2.147463     0.000000
H     -1.239913     2.147463     0.000000
H     -2.479666     0.000000     0.000000
H     -1.239913    -2.147463     0.000000
H      1.239913    -2.147463     0.000000
"""
```

[Download benzene-acid.oqp](inputs/benzene-acid.oqp)

```bash
openqp benzene-acid.oqp
```

`nmr(gauge=giao,acid=true)` runs the GIAO NMR calculation and also evaluates
the current density on a grid. The run takes about 40 seconds.

## What you get

Besides the NMR shieldings in the log, OpenQP writes four Gaussian cube files:

```text
    ACID cubes written: benzene-acid_acid.cube, benzene-acid_jx.cube, benzene-acid_jy.cube, benzene-acid_jz.cube
```

| File | Contents |
| --- | --- |
| `benzene-acid_acid.cube` | the ACID scalar field |
| `benzene-acid_jx.cube`, `_jy`, `_jz` | the induced current-density vector for a field along z, perpendicular to the ring |

Open `benzene-acid_acid.cube` in OQP Studio Analysis, set the isovalue to 0.05,
and show the surface; the picture above is the Studio 3D viewer at this isovalue. The vector cubes
can be drawn as arrows in OQP Studio 0.2.6 and later, or in VMD or Multiwfn.

## Reading the result

- The isosurface is one connected belt following the six C–C bonds, with no
  breaks between bonds. Continuity shows that the π electrons are delocalized
  around the whole ring. It does not by itself show aromaticity: an
  antiaromatic ring can also give a connected surface.
- Aromatic and antiaromatic rings differ in the direction of the current.
  For **B** along z, a diatropic (aromatic) current circulates clockwise seen
  from the +z side, and a paratropic (antiaromatic) one counter-clockwise (see
  [ACID Current-Density Maps](../workflows/acid.md#reading-the-map)). Averaging
  r × j from `benzene-acid_jx.cube` and `benzene-acid_jy.cube` on circles
  around the ring axis gives a clockwise circulation on the ring (r = 1.4 Å)
  and outside it, both in the ring plane and 0.5–1.0 Å above it: the benzene
  current is diatropic. Only inside the ring in the molecular plane
  (r = 1.0 Å, z = 0) does the circulation reverse, which is the known inner
  paratropic contribution.
- In the ACID literature, saturated rings show surfaces that break into
  separate bond regions at the same isovalue; the cyclohexane run suggested
  below tests this directly.

## Try next

- Run the same calculation for cyclohexane and compare the topology of the
  surface, and for cyclobutadiene and compare the direction of the current
  (draw the vector cubes as arrows, or repeat the r × j average above).
- Change the isovalue in Studio and note the value at which the belt breaks
  apart.

See also: [ACID Current-Density Maps](../workflows/acid.md),
[NMR chemical shifts example](benzene-nmr.md).
