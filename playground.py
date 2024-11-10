def decodeEmail(e):
  de = ""
  k = int(e[:2], 16)

  for i in range(2, len(e)-1, 2):
    de += chr(int(e[i:i+2], 16)^k)

  return de

print(decodeEmail("aac8c4d9c9ddc9eacec6d9df84cfcedf84dac2"))