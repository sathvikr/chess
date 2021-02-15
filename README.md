# chess

This is a chess engine that plays against a user.

Python 3.9 and python-chess were used in this project.

1. Run the program.
2. In app.py, lines 254 to 257 will look like this. The program runs on the web by default.

if __name__ == '__main__':
    # main()
    app.debug = True
    app.run(host="localhost", port=8080)

3. If you want to run it as a normal python script, modify these lines (254 - 257) in app.py to look like this.

if __name__ == '__main__':
    main()
    # app.debug = True
    # app.run(host="localhost", port=8080)

4. If you choose to run it as a web application, click the link (http://localhost:8080/) to open the GUI. It will open in a seperate window.
