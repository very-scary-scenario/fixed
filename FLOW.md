# game loop

- host visits site, hits go, asks server for new game
- server responds with the host webapp and a session cookie
- host shows lobby key and go button on screen
- players visit site, enter code, hit go
- server validates game code, issues session cookie
- host hits go, asks server for categories
- host shows list of some categories, host picks one, tells server which was picked
- server responds with a prompt, host shows prompt
- players fill out their text box and hit submit, however many times they like
- once time is up, the host asks the server for everything that was submitted
- the server sends the host everything that was sent by clients, as a changelog entry, and also a subset of categories again
