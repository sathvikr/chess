# red_chess

1. Run the program as a normal python script.
2. In app.py, lines 254 to 257 will look like this. The program runs on the computer by default.

if __name__ == '__main__':
    main()
    # app.debug = True
    # app.run(host="localhost", port=8080)

3. If you want to run it as a web application, modify these lines (254 - 257) in app.py to look like this.

if __name__ == '__main__':
    # main()
    app.debug = True
    app.run(host="localhost", port=8080)

4. If you choose to run it as a web application, click the link (http://localhost:8080/) to open the GUI. It will open in a seperate window.
