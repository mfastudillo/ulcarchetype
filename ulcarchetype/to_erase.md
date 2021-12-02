Minor remark: in the workplan, section 2.2 you mention 5 elements and then list only 4. I guess there might be a homepage element with miscellaneous information missing?

Major remark 1: I saw somewhere a comment that you don't want to do the API because that is 'back-end'.

In the context of this project the back-end is developed by everyone else except WP3.2 and WP4.3, calculations take place in the Strato New cluster, its input are raw (manual, scraped and contributed) data and its output are results' tables and files.

The front-end is developed by WP3.2 and WP4.3, computation takes place in a VMware server with a public IP, its inputs are the results' tables and files and its output are responses to user requests.

An API is a user interface so whichever way you want to look at it fits in the definition of front-end above. If you want to change the terminology let us know.

Major remark 2: I didn't notice request configurations in the workplan, and they are a central key in the architecture.

The architecture that was earlier agreed upon was to have 3 main functionalities: calculate, explore, contribute.

In each of these functionalities there is similar pipeline: receive and validate request configuration; process request configuration.

The medium by which the request configuration is obtained can be through html forms, configuration file or API. For some specific requests it might be possible to hover/drag/click using fancy visual tricks.

The request configuration as a stand-alone entity is critical, so that requests can be tweaked and automated, and also so that WP3.2 and WP1.2 can agree on the lexicon and syntax for matters that require interaction between back- and front-end and the database.

Major remark 3: You are considering the API as a separate 'element'.

That does not make sense. As I wrote above, there are three functionalities and three main media for making the request. The API is a medium: it falls in the same category as html forms or submitting configuration files, it is orthogonal to the calculate/explore/contribute functionalities.

Major remark 4: You don't want to build the API, but someone else should do it.

I also don't understand your allergy to APIs. It is possible to make them directly in Django (https://www.django-rest-framework.org/tutorial/quickstart/) or otherwise you can use Falcon or move the entire project to Flask. But whichever team is making the website should also do the API.

Major remark 5: You don't want to do data validation.

I am sorry but that is whining. Data validation may be boring but it is part of software development. Look at the coordination_architecture.py I prepared to assemble the WP diagrams. Probably 80% of it is data validation. It's not the most exciting thing to do but it's part of the job. To validate request configurations and user contributions you just need to write a bunch of try/except statements and meaningful error messages.

The particular file formats and syntax need to be defined upfront but it has to be done, and it has to be done by WP3.2. If the two of you don't want to do it it means you don't want to do WP3.2

Major remark 6: The work plan is not agile.

The philosophy of the project (and this was not my decision) is to have all parts moving in parallel, and have a working prototype early on (the deadline was now, but I guess everything was posptponed 6 months) that is later refined. In your work plan you want to spend three months doing literature surveys and benchmarking and only start coding in the second half of 2022... That cannot be. You need to start now and have something that you can to stakeholders as soon as possible. If don't have something concrete for them to comment/grasp you will not have useful feedback and the project deadline will arrive and you won't have started doing actual work.

Remember: no battle plan survives contact with the first bullet. You need to start working on a prototype, and get feedback to improve it. When you start doing stuff you will see that new challenges will pop up and challenges that you considered critical are not that important. 

Related to this, we don't the need to explore and use complex and sophisticated - and possibly poorly supported - software. Let's stick to Django or Flask and then start doing stuff. When the framework is lacking for some reason then use whatever is the most popular solution to that particular problem. But start solving actual problems!