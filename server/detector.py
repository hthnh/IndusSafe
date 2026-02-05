def detect_fault(data):
    faults = []

    voltages = [data.U1, data.U2, data.U3]
    currents = [data.I1, data.I2, data.I3]

    # Mất pha
    if any(v < 50 for v in voltages):
        faults.append("Mất pha")

    # Lệch áp
    avg_u = sum(voltages) / 3
    if any(abs(v - avg_u) / avg_u > 0.15 for v in voltages):
        faults.append("Lệch pha")

    # Quá áp / thấp áp
    if any(v > 250 for v in voltages):
        faults.append("Quá áp")
    if any(v < 180 for v in voltages):
        faults.append("Thấp áp")

    # Quá dòng
    if any(i > 1.3 * max(currents) for i in currents):
        faults.append("Quá dòng")

    return faults
