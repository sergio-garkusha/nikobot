a = "#️⃣ 5678"
b = "#️⃣7777"
c = "#️⃣ 9999\n"

a = a.replace('#️⃣', '')
b = b.replace('#️⃣', '')
c = c.replace('#️⃣', '')

print(int(a), int(b), int(c))
