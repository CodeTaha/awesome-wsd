# Team
###### Thuy Nguyen - 547288
###### Ninh Truong - 547961
###### Taha Kachwala - 548494

# Features Implemented
### Core Features

##### Authentication: 200 points
Login, logout and register (both as player or developer).
Email validation sent from Gmail SMTP-server, using Django's Core Backend SMTP
Use Django auth

##### Basic player functionalities: 300 points
Buy games, payment is handled by a mockup payment service
Play games, including Save State/Load State/Save Highscore
Security restrictions, e.g. player is only allowed to play the games they’ve purchased,   anonymous user can only allowed to buy the games after signing in.
Find related games based on categories. Games have categories (action, adventure, strategy, etc) and labels (Editor’s Top Picks, Hot, Promotion, etc)

##### Basic developer functionalities: 200 points
Add a game, set price and manage game
Basic game inventory and sales statistics
Security restrictions, e.g. developers are only allowed to modify/add/etc. their own games

##### Game/service interaction: 200 points
Save Player’s High Score
Save Game state
Load Game state

##### Quality of Work 100 points
Quality of code (structure of the application, comments)
Purposeful use of framework, use REST backend API, front-end calls APIs using ajax
Sleek and modern UI, smooth User Experience
Meaningful automated test cases for api calls and views

##### Non-functional requirements 200 points
Project plan (part of final grading, max. 50 points)
Setup guide, demo checklist, progress tracking document on Google Drive
(https://drive.google.com/drive/u/0/folders/0B6Mc9WV9-SgjTkVvNVhOMGlYaGs)

### Additional Features

##### Save/load and resolution feature : 100 points
The service supports saving and loading for games with the simple message protocol described in Game Developer Information

##### RESTful API: 100 points
All backend API calls are REST

##### Own game: 30 points (out of 100)
Develop a simple game in JavaScript that communicates with the service (save highscore), awesomegames/games/circles.html

##### Mobile Friendly: 50 points (Fully responsive)
##### Share on Facebook: 50 points

### TOTAL SCORE: 1530

# Challenges and Strengths

### Challenges

##### Backend:
Using Django REST Framework is convenient but can be challenging because we didn’t find many answers on Stackoverflow when we encounter a problem. We spent quite some time in the beginning to figure out how to use it. But once we understood and knew how to use it, we were able to build the backend API quickly.

##### Frontend:
All three of us don’t have design background. To come up with the design of this gamestore, our “designer” Ninh had to spend a lot of time to gather ideas and inspiration from many sources. Most of the effects and styles (transition, hide/show, etc.) are custom made by Ninh.

##### Deployment:
There was problem with static folder that all styling was not applicable. Eventually we solved this by using Whitenoise

##### Collaboration:
We should have 2 separate view files, 1 for front end and 1 for back end so that we don’t have to resolve conflicts all the time as we all work on the same file.

##### Own game development:
we were not familiar with js game development so we couldn’t create a good game. We did have a very simple game, user can save highscore but save/load state is not implemented. To populate data for the game store, we took information (name, description, images) from Google’s Play Store.

### Strengths

Using REST backend and ajax calls on frontend which helps reduce frontend/backend coupling.
Backend APIs can be tested quickly using a Rest client (e.g. Postman) without waiting for views/screen to be implemented
Backend returns serialized data in json format and the client side can easily convert JSON data into native JavaScript objects
Bootstrap css supports responsive.


# Task Distribution

At a high level, our task distribution is as follows:
Thuy - Backend: Models Design and Core APIs.
Ninh - Frontend Design and pages (including Game Service and iframe interaction).
Taha - Payment System (both frontend and backend) and Game development, Developer’s Sales Statistics.

For detailed tasks, please see the list of issues and commits on Niksula at:
https://git.niksula.hut.fi/kachwat1/wsdproject/issues?label_name=&milestone_id=&scope=&state=all

# Deployment

### Heroku link: http://awesome-wsd.herokuapp.com

### Instructions:
After a new user (either as developer or player) is registered, a new user is created with is_active = False. At this point, the user cannot yet sign in the system. She needs to activate her account by clicking on the email verification link sent to the email address.
The The UI is intuitive and easy to navigate. Users should be able to perform all the implemented functionalities just by using the web app without any extra instructions.

### To use our demo data:
##### Developer accounts:
Username: ninh, password: root
Username: thuyn, password: root
Username: taha, password: root

##### Player accounts:
Username: player1, password: root
Username: player2, password: root
Username: inactive_test, password: root (user with is_active=False to test signin fail)

##### Admin:
To access admin dashboard: http://awesome-wsd.herokuapp.com/admin
Admin account: Username: admin, password: adminadmin

########################################################################################################################
########################################################################################################################
########################################################################################################################

# Awesome WSD Project plan

### 1. Team
* **548494** Taha Kachwala
* **547288** Thuy Nguyen
* **547961** Ninh Truong

### 2. Goal
Building an online store for Javascript games using Django, Jquery & Bootstrap.

With the system, user can register as one of the following roles:
  * **Game developer**: add games to their inventory, see list of game sales
  * **Player**: buy games, play games, record their scores and see game high scores.

These basic features will be fully developed in 7 weeks, from 04/01/2016 to 20/02/2016.

### 3. Plan

We break down the tasks into following core activities:

 - Requirements and Planning
   * Requirement analysis
   * Project planning
 - Design
   * Database & sitemap
   * Layout: pages sketch & prototypes
 - Development
   * Front-end development
   * Back-end development
   * Content: add games, photos, replace dummy text by real text.
 - Testing
 - Deployment (build MVP)

We will follow SCRUM for agile and iterative development with 2-week sprints. At the end of a sprint, we should have a MVP deployed. We will have at least one weekly meeting every Monday for project updates, review and retrospectives:

 - What has the team done since we last met?
 - What will the team do before we meet again?
 - Is anything slowing our team down or getting in their way?


### 4. Process and Time Schedule

- Weeks 1 (04/01 to 10/01):
  * Research, planning & design
  * Setup project and database - using default sqlite db.
- Weeks 2-3 (11/01 to 24/01): Sprint 1 - MVP goals:
  * Register and Login: User can register with two different roles using facebook or google account, and login
  * Game list : any users without logging in can see the list of all games, using dummy data
  * The developers can add game, using dummy data
  * Test and debug
- Weeks 4-5 (25/01 to 07/02): Sprint 2 - MVP goals:
  * Developers can see his own added games
  * Player can buy games. Shopping cart implemented
  * Players can see list of games owned and play games
  * Test and debug
- Week 6-7 (08/02 - 20/02): Last sprint - MVP goals:
  * Players can play game and save scores
  * Players can see games owned and high scores for those games
  * Content, games, users are added
  * Look and feel polished.
  * More test and debug


### 5. Testing
* Bottom-up development: Write automated test script before coding.
* Every module is cross-reviewed by other team members.

### 6. Risk Analysis
For the first half of the development time, the team will work remotely. Our weekly meeting is conducted via Skype.