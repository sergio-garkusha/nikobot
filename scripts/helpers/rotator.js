u = "ua.nikovolunteers.bot";
p = "u@-1s-fri&nd.ly";

high = 128;
low = 64;

while (true) {
  rnd = Math.random() * (high - low) + low;
  num = Math.floor(rnd);

  round = btoa(num);
  b64A = btoa(p)

  res = ""
  for (i = 0; i < num; i++) {
    res += b64A + round;
  }

  end = atob(res)

  g = end.slice(0, num - 64)
  if (g.length >= 20) {
    console.log(g, num)
    break;
  }
}

user = { uname: u, pass: res, q: num }
console.log(JSON.stringify(user));
// db.users.insertOne(

// console.log(atob(l));
// console.log(end.slice(0, num - 64));

// 'u@-1s-fri&nd.ly115u@-1s-fri&nd.ly115u@-1s-fri&nd.ly'
// 'u@-1s-fri&nd.ly115u@-1s-fri&nd.ly115u@-1s-fri&nd.ly'
