# A bot that automates the search for applications
## Бот що автоматизує пошук заявок


> Commands:
```
start - Знайомство
create_order - Створити заявку
find_by_phone - Шукати за номером телефону
find_by_name - Шукати за ім'ям
find_by_dob - Шукати за датою народження
find_by_address - Шукати за адресою
help - Докладний перелік можливостей
```

#### TODO:
- [x] Implement `create_order` task
- [x] Implement Descending order for all search results
- [x] Check that user belongs to NikoVoluneers (Naive)
- [x] Check that user belongs to NikoVoluneers (Proper)
- [x] Parser fails on Names with ' sign in Ukrainian, e.g. В'юн В'ячеслав Дем'янович
- [x] `find_by_name` fails on Names with ‘ sign.
- [ ] Add search by name chunks, e.g. Захарч Волод Олекс
- [ ] Implement `CANCEL` command ?
- [ ] Improve search by address (See below)
- [ ] Add inline `joint_search`, e.g. /joint_search p=0990000999 d=12.31.1995 n=(...) a=(...)
107. PROFIT!!!111

#### Notes and thoughts
Search by address is far from ideal based on data we have.
So it is most realistic to search by street names with $regex.
That will generate many results (20 +)
    
1. Create mechanism for this < Вулиця + 16 + кв 5 >
    1. Searches within prev results


        ```result = search (Вулиця):
            # narrows the scope by adding house number
            search (16):
                # narrows the scope by adding house number
                search (кв 5):
                    ...
                    # exact result```
    2. OR Add InlineKeyboard to create choosable address cards
        1. Update to latest version:
               `pip install python-telegram-bot==v20.0a2`
        2. Revrite the WHOLE APP accordingly :(
"""

#### Misc
- [How to Setup Python Script Autorun As a Service in Ubuntu](https://websofttechs.com/tutorials/how-to-setup-python-script-autorun-in-ubuntu-18-04/)
- [How to Detach Unix Process](https://www.tecmint.com/run-linux-command-process-in-background-detach-process/)


 <!--
# import .json into db
docker cp parsed_results.json mongodb:/tmp/parsed_results.json
docker exec mongodb mongoimport -d nikovolunteers -c orders --file /tmp/parsed_results.json --jsonArray

# export .json from db
mongoexport -d nikovolunteers -c orders --out output.json
docker cp mongodb:/output.json . # mongodb is the name of my local container

docker ps -a
docker exec -it mongodb bash

db.orders.find({"Phone": 680659203}).pretty()
db.orders.find({"Date": {$in: [/2022-08-03/]}}).count()

db.orders.find({"Cathegories": {$in : ["Пенсіонер"]}}).count()
db.orders.find({"PIB": {$in: ["Михеевич"]}}).pretty()
db.orders.find({"PIB": {$all: ["Владимир", "Васильевич"]}}).pretty()

db.orders.find({"Bday": {$in: [/5 лют 1987/]}}).count()
db.orders.find({"Bday": {$in: [/^5 лют/]}}).count()
db.orders.find({"Bday": {$in: [/^1942/]}}).count()
db.orders.find({"Bday": {$in: [/1942/]}}).count()

db.orders.find({"Address": {$in: [/Партизанской/]}}).count()

# Import cert
scp X509-cert.pem <user_name>@<server_name>:/var/www/

/lib/systemd/system/nikobot.py.service
systemctl enable nikobot.py.service 
systemctl start nikobot.py.service
systemctl status nikobot.py.service
-->
