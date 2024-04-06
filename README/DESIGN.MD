# DESIGN



## Features
Feature | Description
--- | --- 
Google Login | Enables users to authenticate using Google OAuth2 for secure and convenient login experience.
email login | Enables users to authenticate using email and password for secure and convenient login experience.
JWT | Provides secure authentication and authorization using JSON Web Tokens.
Company Profile | Facilitates the creation of comprehensive profiles for companies, allowing them to highlight their mission, values, and key information.
Softwares | Provides functionality for adding and managing software applications along with their corresponding technology stacks, promoting efficient organization and tracking.
Stack | Enables the creation and management of different technology stacks, including programming languages, frameworks, libraries, and tools, ensuring effective categorization and organization of software development resources.
Posts | Empowers users to publish and share content, promoting knowledge sharing and collaboration within the community.
Comments | Facilitates user engagement by allowing them to provide comments and initiate conversations on published content, creating a vibrant and interactive platform.
Google Groups integration | Integrating Google Groups allowing messages from google groups to be imported to the platform


## Used Stacks
The Project is been builded with the following stacks:
Backend: Python, FastApi
Frontend: React
Database: Neo4j
Cache: Redis
 
## Authentication 
Authentication can be done by google oauth or by using form login with email and password, it will generate a JWT token which will be used to validate the user.

## Cache
To speed up the retrieval data a Redis Cache has been implemented.

## Database
A Graph database have been selected for this project as it can be really efficient for recommendation systems, although a recommendation system won’t be used on an initial stage of the application it could be extremely relevant in case the platform grows for and englobes personnel from different areas of the company.

We are currently using Neo4j as database, for more information on Neo4j please see it [Here](NEO4J.MD) 

### Database structure
<img src='README/IMG/Neo4j.png'/>

### Database Schemas
User | Stack | Software 
--- | --- | ---
{<br/>"uid": 'str',<br/>"email": 'str',<br/>"name": 'str',<br/>"preferred_name": 'str',<br/>"role": 'str',<br/>"joined_at": 'datetime',<br/>"twitter": 'str',<br/>"linkedin": 'str',<br/>"github": 'str',<br/>"picture": 'str',<br/>"bio": 'str',<br/>"active": 'boolean',<br/>"is_superuser": 'boolean',<br/>"strenght": 'int',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/>RELATIONSHIPS<br/>"stacks": 'List[Stacks Objs]',<br/>"company": 'Company Obj'<br/>"softwares": 'List[Softwares Objs]'}|{<br/>"uid": 'str',<br/>"name": 'str',<br/>"description": 'str',<br/>"type": 'str',<br/>"image": 'str',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/>"strenght": 'int',<br/><br/>RELATIONSHIPS<br/>"users": 'List[Users Objs]',<br/>"posts": 'List[Posts Objs]',<br/>"softwares": 'List[Softwares Objs]',<br/>"part_of": 'List[Stacks Objs]',<br/>"posts": 'List[Posts Objs]',<br/>"companies": 'List[Companies Objs]'<br/>}|{<br/>"uid": 'str',<br/>"name": 'str',<br/>"client": 'str',<br/>"project_type": 'str',<br/>"problem": 'str',<br/>"solution": 'str',<br/>"comments": 'str',<br/>"link": 'str',<br/>"image": 'str',<br/>"strenght": 'int',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/><br/>RELATIONSHIPS<br/>"users": 'List[Users Objs]',<br/>"company": 'Company Obj'<br/>"stacks": 'List[Stacks Objs]',<br/>"posts": 'List[Posts Objs]'} 

Company | Location
---|---
{<br/>"uid": 'str',<br/>"name": 'str',<br/>"logo": 'str',<br/>"description": 'str',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/>RELATIONSHIPS<br/>"users": 'List[Users Objs]',<br/>"strenght": 'int',<br/>"softwares": 'List[Softwares Objs]',<br/>"stacks": 'List[Stacks Objs]',<br/>"locations": 'List[Locations Objs]'}|{<br/>"uid": 'str',<br/>"country": 'str',<br/>"city": 'str',<br/>"address": 'str',<br/><br/>RELATIONSHIPS<br/>"company": 'Company Obj'}


Post | Comment
---|---
{<br/>"uid": 'str',<br/>"text": 'str',<br/>"image": 'str',<br/>"link": 'str',<br/>"link_title": 'str',<br/>"link_description": 'str',<br/>"link_image": 'str',<br/>"comment_count": 'int',<br/>"likes_count": 'int',<br/>"tags": 'str',<br/>"strenght": 'int',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/><br/>RELATIONSHIPS<br/>"tagged_users": 'List[Users Objs]',<br/>"tagged_softwares": 'List[Softwares Objs]'<br/><br/>"tagged_stacks": 'List[Stacks Objs]',<br/>"tagged_companies": 'List[Companies Objs]',<br/>"comments": 'List[Commments Objs]'<br/>}|{<br/>"uid": 'str',<br/>"comment": 'str',<br/>"comment_count": 'int',<br/>"likes_count": 'int',<br/>"created_at": 'datetime',<br/>"updated_at": 'datetime',<br/><br/>RELATIONSHIPS<br/>"created_by": 'Users Objs',<br/>"c_on_post": 'Post Obj',<br/>"c_on_comment": 'Comment Obj',<br/>"c_comments": 'List[Comments Objs]'}



### Deployment

Dev Environment
Backend: It has been deployed on AWS on a single instance, updates on the code can be easily deployed by pushing the code to the Bitbucket main branch accessing the instance terminal via ssh and running the command “reload” which will run the bash script responsible for making a pull request to Repo, install any new library and reload uvicorn and nginx.

Database: Database is been deployed from within the NEO4J Aurora.

    Any suggestion on how to improve the deployment process is welcome.