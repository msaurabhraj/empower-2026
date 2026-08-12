"""
GOAL / INTENT
-------------
Build tagged data: attaching a small marker to a piece of data that says which representation it is in, so generic code can look at the tag and dispatch to the right representation-specific logic instead of every caller having to know, and check, which representation it happens to be holding. The concrete vehicle is AC circuit impedance, which real test equipment reports in two genuinely different but equally valid forms — rectangular (resistance and reactance) from a network analyzer, and polar (magnitude and phase angle) from an impedance bridge — with neither form being "more correct," just two representations of the same underlying complex number.

TASK / IMPLEMENTATION
----------------------
Implement every function below. Everything from real_part onward must go through the generic selectors defined for that purpose — never by checking a tag directly outside of attach_tag, type_tag, contents, real_part, imag_part, magnitude, or angle.
"""

import math

type Impedance = tuple[str, tuple[float, float]]


def attach_tag(type_tag: str, contents: tuple[float, float]) -> Impedance:
    """Constructor. Attaches a representation tag, 'rectangular' or 'polar', to a raw pair of floats."""
    return (type_tag, contents)


def type_tag(tagged_impedance: Impedance) -> str:
    """Selector."""
    return tagged_impedance[0]


def contents(tagged_impedance: Impedance) -> tuple[float, float]:
    """Selector. Returns the raw, untagged pair of floats underneath a tagged Impedance value."""
    return tagged_impedance[1]


def make_from_real_imag(resistance: float, reactance: float) -> Impedance:
    """Constructor. Builds a rectangular-tagged Impedance from a resistance, the real part, and a reactance, the imaginary part, both in ohms."""
    return attach_tag("rectangular", (resistance, reactance))


def real_part_rectangular(tagged_impedance: Impedance) -> float:
    """Returns the resistance component. Only valid on a rectangular-tagged Impedance."""
    resistance, _ = contents(tagged_impedance)
    return resistance


def imag_part_rectangular(tagged_impedance: Impedance) -> float:
    """Returns the reactance component. Only valid on a rectangular-tagged Impedance."""
    _, reactance = contents(tagged_impedance)
    return reactance


def magnitude_rectangular(tagged_impedance: Impedance) -> float:
    """Returns sqrt(resistance**2 + reactance**2) for a rectangular-tagged Impedance."""
    resistance = real_part_rectangular(tagged_impedance)
    reactance = imag_part_rectangular(tagged_impedance)
    return math.sqrt(resistance**2 + reactance**2)


def angle_rectangular(tagged_impedance: Impedance) -> float:
    """Returns math.atan2(reactance, resistance), the phase angle in radians, for a rectangular-tagged Impedance."""
    resistance = real_part_rectangular(tagged_impedance)
    reactance = imag_part_rectangular(tagged_impedance)
    return math.atan2(reactance, resistance)


def make_from_mag_ang(magnitude: float, angle: float) -> Impedance:
    """Constructor. Builds a polar-tagged Impedance from a magnitude in ohms and a phase angle in radians."""
    return attach_tag("polar", (magnitude, angle))


def magnitude_polar(tagged_impedance: Impedance) -> float:
    """Selector. Only valid on a polar-tagged Impedance."""
    magnitude, _ = contents(tagged_impedance)
    return magnitude


def angle_polar(tagged_impedance: Impedance) -> float:
    """Selector. Only valid on a polar-tagged Impedance."""
    _, angle = contents(tagged_impedance)
    return angle


def real_part_polar(tagged_impedance: Impedance) -> float:
    """Returns magnitude * cos(angle) for a polar-tagged Impedance."""
    return magnitude_polar(tagged_impedance) * math.cos(
        angle_polar(tagged_impedance)
    )


def imag_part_polar(tagged_impedance: Impedance) -> float:
    """Returns magnitude * sin(angle) for a polar-tagged Impedance."""
    return magnitude_polar(tagged_impedance) * math.sin(
        angle_polar(tagged_impedance)
    )


def real_part(tagged_impedance: Impedance) -> float:
    """Returns the resistance regardless of whether tagged_impedance is rectangular- or polar-tagged, dispatching on type_tag to real_part_rectangular or real_part_polar."""
    if type_tag(tagged_impedance) == "rectangular":
        return real_part_rectangular(tagged_impedance)

    if type_tag(tagged_impedance) == "polar":
        return real_part_polar(tagged_impedance)

    raise ValueError(f"Unknown type tag: {type_tag(tagged_impedance)}")


def imag_part(tagged_impedance: Impedance) -> float:
    """Returns the reactance regardless of representation, dispatching on type_tag."""
    if type_tag(tagged_impedance) == "rectangular":
        return imag_part_rectangular(tagged_impedance)

    if type_tag(tagged_impedance) == "polar":
        return imag_part_polar(tagged_impedance)

    raise ValueError(f"Unknown type tag: {type_tag(tagged_impedance)}")


def magnitude(tagged_impedance: Impedance) -> float:
    """Returns the magnitude regardless of representation, dispatching on type_tag."""
    if type_tag(tagged_impedance) == "rectangular":
        return magnitude_rectangular(tagged_impedance)

    if type_tag(tagged_impedance) == "polar":
        return magnitude_polar(tagged_impedance)

    raise ValueError(f"Unknown type tag: {type_tag(tagged_impedance)}")


def angle(tagged_impedance: Impedance) -> float:
    """Returns the phase angle regardless of representation, dispatching on type_tag."""
    if type_tag(tagged_impedance) == "rectangular":
        return angle_rectangular(tagged_impedance)

    if type_tag(tagged_impedance) == "polar":
        return angle_polar(tagged_impedance)

    raise ValueError(f"Unknown type tag: {type_tag(tagged_impedance)}")


def add_impedance(
    first_impedance: Impedance,
    second_impedance: Impedance,
) -> Impedance:
    """Adds two impedance readings regardless of which representation each one arrived in, returning a new rectangular-tagged Impedance, built exclusively out of the generic selectors real_part, imag_part, and make_from_real_imag — never by checking either argument's tag."""
    return make_from_real_imag(
        real_part(first_impedance) + real_part(second_impedance),
        imag_part(first_impedance) + imag_part(second_impedance),
    )


# ------------------------------------------------------------------
# REAL-WORLD SEQUENCE TASK
# ------------------------------------------------------------------

element_one_reading: Impedance = make_from_real_imag(4.0, 3.0)

element_two_reading: Impedance = make_from_mag_ang(
    5.0,
    math.pi / 4,
)

total_series_impedance: Impedance = add_impedance(
    element_one_reading,
    element_two_reading,
)

total_resistance: float = real_part(total_series_impedance)
total_reactance: float = imag_part(total_series_impedance)

print(type_tag(element_one_reading))  # rectangular
print(type_tag(element_two_reading))  # polar

print(round(real_part(element_one_reading), 4))  # 4.0
print(round(magnitude(element_one_reading), 4))  # 5.0

print(round(real_part(element_two_reading), 4))  # 3.5355
print(round(imag_part(element_two_reading), 4))  # 3.5355

print(round(total_resistance, 4))  # 7.5355
print(round(total_reactance, 4))   # 6.5355