from telegram.constants import MAX_MESSAGE_LENGTH


def room_builder_str(available_rooms , until):
    """
    this function take as input the list af all tha available classtooms
    and parse the list into a list of multiple string in order to not exceed the telegram
    len limit
    """
    splitted_msg = []
    available_rooms_str = ""
    for building in available_rooms:
        if  MAX_MESSAGE_LENGTH - len(available_rooms_str) <= 50:
            splitted_msg.append(available_rooms_str)
            available_rooms_str = ""
        available_rooms_str += '\n<b>{}</b>\n'.format(building)
        for room in available_rooms[building]:
            emoji = "🔌" if room['powerPlugs'] else ''
            available_rooms_str += ' <a href ="{}">{:^10}</a> ({} {}) {}\n'.format(room['link'], room['name'], until , room['until'],emoji)

    splitted_msg.append(available_rooms_str)
    return splitted_msg

def formatta_messaggio_risultati(risultati):

    """Crea messaggio Telegram dai risultati nel formato richiesto"""

    

    if 'errore' in risultati:

        return f"❌ Errore: {risultati['errore']}"

    

    # Intestazione richiesta

    # Esempio: 15/10/2025   Milano Città Studi   8-10

    ora_dal, ora_al_search = risultati['orario'].split(' - ')

    h_dal = ora_dal.split(':')[0]

    h_al = ora_al_search.split(':')[0]

    

    header = f"<b>{risultati['data']}   {risultati['sede_nome']}   {h_dal}-{h_al}</b>\n"

    

    if risultati['totale'] == 0:

        return header + "\n😔 Nessuna aula libera trovata"



    # Uniamo aule studio e normali per il raggruppamento

    all_edifici = {}

    

    for ed, aule in risultati['aule_studio'].items():

        if ed not in all_edifici: all_edifici[ed] = []

        all_edifici[ed].extend(aule)

        

    for ed, aule in risultati['aule_normali'].items():

        if ed not in all_edifici: all_edifici[ed] = []

        all_edifici[ed].extend(aule)



    msg = header

    

    # Ordiniamo gli edifici (numerici prima, poi stringhe)

    def sort_key(s):

        if s.startswith("Edificio "):

            try: return (0, int(s.split(" ")[1]))

            except: return (1, s)

        return (1, s)



    for ed in sorted(all_edifici.keys(), key=sort_key):

        msg += f"\n <b>{ed}</b> \n"

        for aula in all_edifici[ed]:

            plug = "🔌" if aula.get('powerPlugs') else ""

            # Il nuovo scraper non ha "fino alle" reale, usiamo l'orario di fine ricerca

            # o cerchiamo di capire se c'è altro. Per ora ora_al della ricerca.

            msg += f"   {aula['sigla']:10} (fino alle {risultati['ora_al']}) {plug}\n"

            

    return msg
