# Calculate AMEX totals
amex_msi = 374.17 + 433.64 + 433.64 + 2250.00 + 432.82 + 562.01 + 802.17 + 687.84 + 777.84 + 5224.79 + 1982.66 + 1157.30
print(f'AMEX MSI Total: ${amex_msi:.2f}')
print(f'AMEX Corrientes: $3178.04')
print(f'AMEX TOTAL: ${amex_msi + 3178.04:.2f}')

banamex_msi = 1664.79 + 151.27
print(f'\nBanamex ORO MSI: ${banamex_msi:.2f}')
print(f'Banamex ORO Corrientes: $2821.70')
print(f'Banamex ORO TOTAL: ${banamex_msi + 2821.70:.2f}')

print(f'\nYTP: $4123.39')

total = (amex_msi + 3178.04) + (banamex_msi + 2821.70) + 4123.39
print(f'\nTOTAL Q1: ${total:.2f}')
