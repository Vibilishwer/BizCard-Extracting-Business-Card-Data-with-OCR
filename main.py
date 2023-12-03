import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as sql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re
import numpy as np
import time


# # SETTING PAGE CONFIGURATIONS

st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR | By VIBILISHWER",
                   page_icon= "https://img.freepik.com/free-vector/colorful-letter-gradient-logo-design_474888-2309.jpg?w=826&t=st=1701247442~exp=1701248042~hmac=b0dc190fa8eb41a049d99ae73fc19969133cd3a1df5c591de397ac4f164c699d",
                   layout= "wide",
                   initial_sidebar_state= "auto",
                   menu_items={'About': """# This OCR app is created by *vibilishwer*!"""})
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)


# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cutewallpaper.org/22/plane-colour-background-wallpapers/189265759.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()

# CREATING OPTION MENU
selected = option_menu(None, ["Home","Upload & Extract","Modify"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password ="root",
                   database= "bizcard"
                  )
mycursor = mydb.cursor(buffered=True)


# mycursor = mydb.cursor()
# mycursor.execute("CREATE TABLE Card_data("
# "id INT AUTO_INCREMENT PRIMARY KEY,"
# "name VARCHAR(255),"
# "designation VARCHAR(255),"
# "company VARCHAR(255),"
# "contact VARCHAR(255),"
# "email VARCHAR(255),"
# "website VARCHAR(255),"
# "address VARCHAR(255),"
# "city VARCHAR(255),"
# "state VARCHAR(255),"
# "pincode VARCHAR(255),"
# "image LONGBLOB )")

# HOME MENU
if selected == "Home":
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("## :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.markdown("## :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
    # with col2:
        # st.image("home.png")
        
# UPLOAD AND EXTRACT MENU
if selected=='Upload & Extract':
    file,text = st.columns([3,2.5])
    with file:
        uploaded_file = st.file_uploader("Choose an image of a business card", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            #original image
            nparr = np.frombuffer(file_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            st.image(image,channels='BGR' ,use_column_width=True)

            #text extraction bounding image 
            if st.button('TEXT BOUNDING'):
                with st.spinner('Detecting text...'):
                    time.sleep(1)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # Apply threshold to create a binary image
                new, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
                # Find contours in the binary image
                contours,new = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # Iterate through each contour and draw it with a different color
                for i in contours:
                    # Get the bounding rectangle coordinates
                    x, y, w, h = cv2.boundingRect(i)
                    # Change the text color to green (BGR format)
                    color = (0, 255, 0)
                    # Draw a rectangle around the contour with the specified color
                    new=cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
                st.write('Compare the images')
                st.image(new,use_column_width=True)
                st.info('Image might be inaccurate detection of text', icon='ℹ️')
  # This is image details to show them...
    with text:
        left,right = st.tabs(['Undefined text extraction','Pre_defined text extraction'])
        with left:
            st.markdown('##### *Here you can view an undefined text extraction using :red[easyOCR]* and this is advanced tool for random text extraction.')
            st.write("Please note: It will accept all image and further update will available soon!")
            if st.button('RANDOM EXTRACTION'):
                with st.spinner('Extracting text...'):
                    reader =easyocr.Reader(['en'])
                    results = reader.readtext(image)
                    for i in results:
                        st.write(i[1])
    
        with right:
            st.markdown("###### *Press below extract button to view structered text format & upload to database Using :blue[easyOCR] & :blue[python regular expression]*")
            st.write('Please note: This tab only for *:blue[business card image]* alone it will not accept random image')
            if st.button('Extract & Upload'):
                with st.spinner('Exracting text...'):
                    reader=easyocr.Reader(['en'])
                    results = reader.readtext(image)
                    card_info = [i[1] for i in results]
                    demilater = ' '
                    #convert to string
                    card = demilater.join(card_info)
                    replacement =[
                        (",",""),
                        (',',''),
                        ("WWW ", "www."),
                        ("www ", "www."),
                        ('www', 'www.'),
                        ('www.', 'www'),
                        ('wwW', 'www'),
                        ('wWW', 'www'),
                        ('.com', 'com'),
                        ('com', '.com'),
                    ] 
                    for old,new in replacement:
                        card = card.replace(old,new)
                    # Phone Details.
                    ph_pattern = r"\+*\d{2,3}-\d{3}-\d{4}"
                    ph = re.findall(ph_pattern,card)
                    Phone = ''
                    for i in ph:
                        Phone = Phone+' '+i
                        card =card.replace(i, '')
                    
                    # Mail_id
                    mail_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}\b"
                    mail = re.findall(mail_pattern, card)
                    Email_id = ''
                    for ids in mail:
                        Email_id = Email_id + ids
                        card = card.replace(ids, '')
                    
                    # website
                    url_pattern = r"www\.[A-Za-z0-9]+\.[A-Za-z]{2,3}"
                    url = re.findall(url_pattern,card)
                    URL = ''
                    for i in url:
                        URL =URL+i
                        card = card.replace(i,'')
                    # Pincode
                    pin_pattern = r'\d+'
                    match = re.findall(pin_pattern,card)
                    Pincode = ''
                    for i in match:
                        if len(i) == 6 or len(i) ==7:
                            Pincode = Pincode+i
                            card = card.replace(i,'')
                    # name,designation,compan_name.
                    name_pattern = r'^[A-Za-z]+ [A-Za-z]+$|^[A-Za-z]+$|^[A-Za-z]+ & [A-Za-z]+$'
                    name_data = []  # empty list
                    for i in card_info:
                        if re.findall(name_pattern, i):
                            if i not in 'WWW':
                                name_data.append(i)
                                card = card.replace(i, '')
                    name = name_data[0]
                    designation = name_data[1]
                    
                    if len(name_data)==3:
                        company = name_data[2]
                    else:
                        company = name_data[2]+' '+name_data[3]
                    card = card.replace(name,'')
                    card = card.replace(designation,'')
                    #city,state,address
                    new = card.split()
                    if new[4] == 'St':
                        city = new[2]
                    else:
                        city = new[3]
                    # state
                    if new[4] == 'St':
                        state = new[3]
                    else:
                        state = new[4]
                    # address
                    if new[4] == 'St':
                        s = new[2]
                        s1 = new[4]
                        new[2] = s1
                        new[4] = s  # swapping the St variable
                        Address = new[0:3]
                        Address = ' '.join(Address)  # list to string
                    else:
                        Address = new[0:3]
                        Address = ' '.join(Address)  # list to string      
                        
                    st.write('')
                    print(st.write('##### :red[Name]       :',name))
                    print(st.write('##### :red[Designation]:',designation))
                    print(st.write('##### :red[company]    :',company))
                    print(st.write('##### :red[Phone]      :',Phone))
                    print(st.write('###### :red[Email_id]  :',Email_id))
                    print(st.write('###### :red[URL]       :',URL))
                    print(st.write('###### :red[Address]   :',Address))
                    print(st.write('###### :red[city]      :',city))
                    print(st.write('###### :red[state]     :',state))
                    print(st.write('###### :red[Pincode]   :',Pincode))
                    
                    Sql = "INSERT INTO card_data(name,designation,company,contact,email,website,address,city,state,pincode,image)"\
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    value = (name,designation,company,Phone,Email_id,URL,Address,city,state,Pincode,file_bytes)
                    mycursor.execute(Sql,value)
                    mydb.commit()
                    st.success('Text Extracted Successfully Upload to Database',icon="☑️")
            
# MODIFY MENU    
if selected == "Modify":
    col1,col2,col3 = st.columns([3,3,2])
    col2.markdown("## Alter or Delete the data here")
    column1,column2 = st.columns(2,gap="large")
    try:
        with column1:
            mycursor.execute("SELECT name FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
                
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute("select company,name,designation,contact,email,website,address,city,state,pincode from card_data WHERE name=%s",
                            (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            company = st.text_input("Company_Name", result[0])
            name = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            contact = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            address = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pincode = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                # Update the information for the selected business card in the database
                mycursor.execute("""UPDATE card_data SET company=%s,name=%s,designation=%s,contact=%s,email=%s,website=%s,address=%s,city=%s,state=%s,pincode=%s
                                    WHERE name=%s""", (company,name,designation,contact,email,website,address,city,state,pincode,selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT card_holder FROM card_data")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to Delete", list(business_cards.keys()))
            st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
            st.write("#### Proceed to delete this card?")

            if st.button("Yes Delete Business Card"):
                mycursor.execute(f"DELETE FROM card_data WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is no data available in the database")
    
    if st.button("View updated data"):
        mycursor.execute("select company,name,designation,contact,email,website,address,city,state,pincode from card_data")
        updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company_Name","Card_Holder","Designation","contact","Email","Website","Area","City","State","Pin_Code"])
        st.write(updated_df)