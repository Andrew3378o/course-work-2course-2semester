CREATE DATABASE IF NOT EXISTS thematic_wiki CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE thematic_wiki;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Guest', 'Editor', 'Admin') DEFAULT 'Guest',
    status ENUM('Active', 'Blocked') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INT DEFAULT NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    content_markdown TEXT NOT NULL,
    category_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE TABLE revisions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT NOT NULL,
    author_id INT NOT NULL,
    old_content TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE article_tags (
    article_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

CREATE TABLE media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    article_id INT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE SET NULL
);

INSERT INTO categories (id, name, parent_id) VALUES
(1, 'Science & Nature', NULL),
(2, 'Technology & Computing', NULL),
(3, 'Arts & Culture', NULL),
(4, 'History & Events', NULL),

(5, 'Physics', 1),
(6, 'Biology', 1),
(7, 'Chemistry', 1),
(8, 'Astronomy & Space', 1),
(9, 'Earth Sciences', 1),
(10, 'Mathematics', 1),

(11, 'Programming', 2),
(12, 'Artificial Intelligence', 2),
(13, 'Cybersecurity', 2),
(14, 'Hardware & Architecture', 2),
(15, 'Web Development', 2),
(16, 'Data Science', 2),

(17, 'Literature', 3),
(18, 'Cinema & Television', 3),
(19, 'Music', 3),
(20, 'Visual Arts', 3),
(21, 'Philosophy', 3),

(22, 'Ancient History', 4),
(23, 'Medieval History', 4),
(24, 'Modern History', 4),
(25, 'Military History', 4),
(26, 'Contemporary Events', 4);

/* example of articles

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE article_tags;
TRUNCATE TABLE tags;
TRUNCATE TABLE articles;

SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO tags (id, name) VALUES
(1, 'programming'),
(2, 'artificial-intelligence'),
(3, 'cybersecurity'),
(4, 'hardware'),
(5, 'web-development'),
(6, 'data-science'),
(7, 'technology'),
(8, 'networking'),
(9, 'software');

INSERT INTO articles (id, title, content_markdown, category_id) VALUES
(1, 'Scientific Method', '**The scientific method** is an empirical method for acquiring knowledge that has characterized the development of science since at least the 17th century. It involves careful observation and applying rigorous skepticism about what is observed.', 1),
(2, 'Nature', '**Nature** can refer to the phenomena of the physical world, and also to life in general. The study of nature is a large part of science, encompassing disciplines like [[Biology]] and [[Physics]].', 1),
(3, 'Natural Science', '**Natural science** is a branch of science concerned with the description, understanding and prediction of natural phenomena. It is divided into life sciences and physical sciences.', 1),

(4, 'Technology', '**Technology** is the application of conceptual knowledge for achieving practical goals, especially in a reproducible way. The word technology can also mean the products resulting from such efforts, including both tangible tools such as utensils or machines, and intangible ones such as software.

## Historical Development
The use of technology began with the conversion of natural resources into simple tools. The prehistoric discovery of how to control fire and the later [[Neolithic Revolution]] increased the available sources of food, and the invention of the wheel helped humans to travel in and control their environment. 

## Impact on Society
Technology has affected society and its surroundings in a number of ways:
1. **Economic Growth:** Technology has helped develop more advanced economies (including today''s global economy).
2. **Communication:** Developments in [[Information Technology]] and the [[World Wide Web]] have lowered barriers to communication.
3. **Daily Life:** Has fundamentally altered how people interact, work, and learn.

## Future Horizons
The latest technological developments, including [[Artificial Intelligence]], [[Machine Learning]], and quantum computing, have the potential to change the world even more drastically.', 2),

(5, 'Computer', '**A computer** is a machine that can be programmed to carry out sequences of arithmetic or logical operations automatically. Modern digital electronic computers can perform generic sets of operations known as programs.

## Core Components
A modern computer typically consists of at least one processing element, typically a [[Central Processing Unit]] (CPU), and some form of memory, like [[Random-Access Memory]] (RAM).
* **CPU:** The brain of the computer that executes instructions.
* **RAM:** Fast, volatile storage for active processes.
* **Storage:** Hard drives or SSDs for long-term data retention.
* **Motherboard:** The main circuit board connecting all components.

## Evolution
Early computers were meant to be used only for calculations. Simple manual instruments like the abacus have aided people in doing calculations since ancient times. Early in the [[Industrial Revolution]], some mechanical devices were built to automate long tedious tasks, such as guiding patterns for looms. More sophisticated electrical machines did specialized analog calculations in the early 20th century.

## Types of Computers
Computers come in various physical forms:
1. **Personal Computers (PCs):** Desktops and laptops intended for individual use.
2. **Servers:** Powerful machines designed to provide services to other computers over a network.
3. **Mobile Devices:** Smartphones and tablets, which are currently the most common type of computers globally.', 2),

(6, 'Information Technology', '**Information technology (IT)** is the use of computers to store, retrieve, transmit, and manipulate data or information. IT is typically used within the context of business operations as opposed to personal or entertainment technologies.

## Scope of IT
IT is considered to be a subset of information and communications technology (ICT). An information technology system (IT system) is generally an information system, a communications system, or, more specifically speaking, a computer system — including all hardware, software, and peripheral equipment — operated by a limited group of IT users.

## Key Disciplines
The field of IT encompasses several specialized domains:
* **[[Computer Security]]:** Protecting information from unauthorized access.
* **Network Administration:** Managing the connectivity between different devices.
* **Database Management:** Overseeing systems that store data, heavily relying on [[Data Science]] concepts.
* **[[Web Development]]:** Creating and maintaining web-based applications.

## Business Impact
In the modern corporate world, IT is the backbone of almost all operations. From automating payroll to leveraging [[Artificial Intelligence]] for customer service, IT departments ensure that technological infrastructure aligns with business goals.', 2),

(7, 'Art', '**Art** is a diverse range of human activity, and resulting product, that involves creative or imaginative talent expressive of technical proficiency, beauty, emotional power, or conceptual ideas.', 3),
(8, 'Culture', '**Culture** is an umbrella term which encompasses the social behavior, institutions, and norms found in human societies, as well as the knowledge, beliefs, and arts of the individuals in these groups.', 3),
(9, 'Humanities', '**Humanities** are academic disciplines that study aspects of human society and culture. In the Renaissance, the term contrasted with divinity and referred to what is now called classics.', 3),

(10, 'History', '**History** is the study and the documentation of the past. Events occurring before the invention of writing systems are considered prehistory. It includes periods like the [[Roman Empire]] and the [[Middle Ages]].', 4),
(11, 'Timeline of human history', 'The **timeline of human history** comprises the narrative of humanity''s past. It is often divided into broad epochs: [[Ancient History]], [[Medieval History]], and [[Modern History]].', 4),
(12, 'Historiography', '**Historiography** is the study of the methods of historians in developing history as an academic discipline, and by extension is any body of historical work on a particular subject.', 4),

(13, 'Quantum Mechanics', '**Quantum mechanics** is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles.', 5),
(14, 'DNA', '**Deoxyribonucleic acid (DNA)** is a polymer composed of two polynucleotide chains that coil around each other to form a double helix. It carries genetic instructions for the development and functioning of all known organisms.', 6),
(15, 'Periodic Table', '**The periodic table** is a tabular display of the chemical elements, which are arranged by atomic number, electron configuration, and recurring chemical properties.', 7),
(16, 'Solar System', '**The Solar System** is the gravitationally bound system of the Sun and the objects that orbit it. It formed 4.6 billion years ago from the gravitational collapse of a giant interstellar molecular cloud.', 8),
(17, 'Geology', '**Geology** is a branch of Earth science concerned with both the liquid and solid Earth, the rocks of which it is composed, and the processes by which they change over time.', 9),
(18, 'Calculus', '**Calculus** is the mathematical study of continuous change, in the same way that geometry is the study of shape, and algebra is the study of generalizations of arithmetic operations.', 10),

(19, 'Python', '**Python** is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected.

## History and Development
Python was conceived in the late 1980s by Guido van Rossum at Centrum Wiskunde & Informatica (CWI) in the Netherlands as a successor to the ABC programming language. Python 2.0 was released in 2000, and Python 3.0 in 2008.

## Programming Paradigms
Python supports multiple programming paradigms:
* **[[Object-Oriented Programming]]:** Classes and objects are core to Python.
* **Procedural Programming:** Supported via built-in functions.
* **Functional Programming:** Supported via `lambda`, `map()`, `filter()`, and `reduce()`.

## Widespread Usage
Due to its large standard library and active community, Python is the dominant language in several fields:
1. **[[Machine Learning]] & AI:** Libraries like TensorFlow and PyTorch.
2. **[[Data Science]]:** Libraries like Pandas and NumPy.
3. **[[Web Development]]:** Frameworks like Django and Flask.

## Example Code
```python
def greet_user(name):
    """A simple greeting function"""
    message = f"Welcome to the thematic wiki, {name}!"
    print(message)

greet_user("Developer")
```', 11),

(20, 'JavaScript', '**JavaScript**, often abbreviated as JS, is a programming language that is one of the core technologies of the [[World Wide Web]], alongside [[HTML]] and [[CSS]]. Over 97% of websites use JavaScript on the client side for web page behavior.

## Core Characteristics
JavaScript is a high-level, often just-in-time compiled language that conforms to the ECMAScript standard. It has dynamic typing, prototype-based object-orientation, and first-class functions.

## Client-Side and Server-Side
Initially, JS was used solely to make web pages interactive in the browser (client-side). However, with the introduction of Node.js, JavaScript is now widely used for server-side [[Web Development]] as well.

## Frameworks and Ecosystem
The JavaScript ecosystem is massive, featuring popular libraries and frameworks:
* **React:** A declarative, efficient, and flexible library for building user interfaces.
* **Angular:** A component-based framework for building scalable web applications.
* **Vue.js:** An approachable, versatile, and performant framework.

## Syntax Example
```javascript
// Fetching data asynchronously
async function fetchArticle(id) {
    try {
        let response = await fetch(`/api/articles/${id}`);
        let data = await response.json();
        console.log(data.title);
    } catch (error) {
        console.error("Error fetching article:", error);
    }
}
```', 11),

(21, 'Object-Oriented Programming', '**Object-Oriented Programming (OOP)** is a programming paradigm based on the concept of "objects", which can contain data and code: data in the form of fields (often known as attributes or properties), and code, in the form of procedures (often known as methods).

## The Four Pillars of OOP
To be considered truly object-oriented, a language or structure must implement four main principles:

1. **Encapsulation:** The bundling of data with the methods that operate on that data. It restricts direct access to some of an object''s components.
2. **Abstraction:** Hiding complex implementation details and showing only the essential features of the object.
3. **Inheritance:** A mechanism wherein a new class is derived from an existing class, inheriting its properties and behaviors.
4. **Polymorphism:** The ability of different objects to respond, each in its own way, to identical messages (or method calls).

## Popular OOP Languages
Many modern programming languages support OOP, including:
* [[Python]]
* Java
* C++
* C#
* [[JavaScript]] (via prototypes or ES6 classes)

Understanding OOP is crucial for [[Web Development]] and structuring complex software architectures.', 11),

(22, 'Machine Learning', '**Machine learning (ML)** is a field of inquiry devoted to understanding and building methods that "learn", that is, methods that leverage data to improve performance on some set of tasks. It is seen as a part of [[Artificial Intelligence]].

## Core Approaches
Machine learning algorithms build a model based on sample data, known as training data, in order to make predictions or decisions without being explicitly programmed to do so. The main types are:

* **Supervised Learning:** The computer is presented with example inputs and their desired outputs, given by a "teacher", and the goal is to learn a general rule that maps inputs to outputs.
* **Unsupervised Learning:** No labels are given to the learning algorithm, leaving it on its own to find structure in its input. Used extensively in [[Data Mining]].
* **Reinforcement Learning:** A computer program interacts with a dynamic environment in which it must perform a certain goal (such as playing a game). It is provided feedback in terms of rewards and punishments as it navigates its problem space.

## Technologies Used
ML relies heavily on mathematical optimization, statistics, and probability. The most common programming language for ML research and deployment today is [[Python]], thanks to libraries like Scikit-Learn and an active community.

## Real-world Applications
ML is used in email filtering, computer vision, [[Natural Language Processing]], medicine, and agriculture.', 12),

(23, 'Artificial Neural Network', '**Artificial neural networks (ANNs)**, usually simply called neural networks (NNs) or neural nets, are computing systems inspired by the biological neural networks that constitute animal brains.

## Architecture
An ANN is based on a collection of connected units or nodes called artificial neurons, which loosely model the neurons in a biological brain. Each connection, like the synapses in a biological brain, can transmit a signal to other neurons.

A neural network typically consists of:
1. **Input Layer:** Receives the initial data.
2. **Hidden Layers:** One or more layers where mathematical computations occur. Networks with multiple hidden layers are called "Deep Learning" networks.
3. **Output Layer:** Produces the final prediction or classification.

## Training Process
Neural networks learn through a process called backpropagation. They adjust the weights of their connections based on the error of their previous predictions. This requires vast amounts of computational power, often utilizing specialized [[Hardware]] like GPUs.

## Role in Modern AI
ANNs are the driving force behind modern [[Machine Learning]] breakthroughs, enabling advanced [[Natural Language Processing]], image recognition, and autonomous driving.', 12),

(24, 'Natural Language Processing', '**Natural Language Processing (NLP)** is an interdisciplinary subfield of linguistics, computer science, and [[Artificial Intelligence]] concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.

## Key Challenges
The goal is a computer capable of "understanding" the contents of documents, including the contextual nuances of the language within them. Main challenges include:
* **Speech Recognition:** Converting spoken language into text.
* **Natural Language Understanding (NLU):** Determining the intended meaning of text.
* **Natural Language Generation (NLG):** Generating text that reads naturally to humans.

## Techniques and Models
Historically, NLP used rule-based systems. Today, it almost entirely relies on [[Machine Learning]] and [[Artificial Neural Network]] models. The invention of the Transformer architecture in 2017 revolutionized the field, leading to Large Language Models (LLMs).

## Common Applications
* Machine Translation (e.g., Google Translate)
* Sentiment Analysis (analyzing customer reviews)
* Chatbots and Virtual Assistants
* Text summarization

[[Python]] is the industry standard for NLP development.', 12),

(25, 'Computer Security', '**Computer security**, cybersecurity, or information technology security (IT security) is the protection of computer systems and networks from information disclosure, theft of or damage to their [[Hardware]], software, or electronic data, as well as from the disruption or misdirection of the services they provide.

## The CIA Triad
The core principles of information security are commonly referred to as the CIA triad:
1. **Confidentiality:** Ensuring that data is accessed only by authorized individuals (often achieved via [[Cryptography]]).
2. **Integrity:** Ensuring that data is accurate and has not been tampered with.
3. **Availability:** Ensuring that systems and data are available to authorized users when needed.

## Threat Landscape
The field is constantly evolving due to new threats:
* **[[Malware]]:** Malicious software like viruses and ransomware.
* **Social Engineering:** Manipulating people into giving up confidential info (e.g., phishing).
* **DDoS Attacks:** Overwhelming servers to make them unavailable.

## Defense Mechanisms
Cybersecurity professionals use firewalls, intrusion detection systems, and strict access controls to protect [[Information Technology]] infrastructure.', 13),

(26, 'Cryptography', '**Cryptography** is the practice and study of techniques for secure communication in the presence of adversarial behavior. More generally, cryptography is about constructing and analyzing protocols that prevent third parties or the public from reading private messages.

## Modern Cryptography
Modern cryptography intersects the disciplines of mathematics, [[Computer]] science, electrical engineering, communication science, and physics. It is a cornerstone of [[Computer Security]].

## Main Types of Cryptography
1. **Symmetric-key Cryptography:** Both the sender and receiver share the same key to encrypt and decrypt the message. It is fast but requires a secure way to share the key initially.
2. **Public-key (Asymmetric) Cryptography:** Uses a pair of keys: a public key for encryption and a private key for decryption. This solves the key distribution problem.
3. **Hash Functions:** One-way mathematical algorithms that take an input and produce a fixed-size string of bytes. Used for verifying data integrity.

## Applications
Cryptography ensures the security of the [[World Wide Web]] via protocols like HTTPS/TLS. It is also the underlying technology behind cryptocurrencies and secure messaging apps.', 13),

(27, 'Malware', '**Malware** (a portmanteau for malicious software) is any software intentionally designed to cause disruption to a [[Computer]], server, client, or computer network, leak private information, gain unauthorized access to information or systems, deprive access to information, or which unknowingly interferes with the user''s computer security and privacy.

## Common Types of Malware
* **Viruses:** Programs that infect other files and replicate when those files are executed.
* **Worms:** Standalone software that replicates without human intervention to spread to other computers.
* **Trojan Horses:** Malware disguised as legitimate software to trick users into installing it.
* **Ransomware:** Encrypts the victim''s data and demands payment (ransom) to restore access. Uses advanced [[Cryptography]].
* **Spyware:** Secretly monitors and collects user data.

## Prevention
Protecting against malware is a primary focus of [[Computer Security]]. Defenses include using reputable antivirus software, keeping operating systems updated, and training users to recognize phishing attempts.', 13),

(28, 'Central Processing Unit', '**A central processing unit (CPU)**, also called a central processor, main processor or just processor, is the electronic circuitry that executes instructions comprising a computer program. The CPU performs basic arithmetic, logic, controlling, and input/output (I/O) operations specified by the instructions in the program.

## Architecture
Modern CPUs are microprocessors, meaning they are contained on a single integrated circuit (IC) chip. The primary components of a CPU include:
* **Arithmetic Logic Unit (ALU):** Performs arithmetic and bitwise logical operations.
* **Registers:** Supply operands to the ALU and store the results of ALU operations.
* **Control Unit:** Orchestrates the fetching (from memory) and execution of instructions.

## Performance Factors
A CPU''s performance is determined by several factors:
1. **Clock Rate:** The speed at which it executes instructions, measured in Gigahertz (GHz).
2. **Cores:** Most modern CPUs are "multi-core", meaning they have multiple independent processing units on the same chip, allowing for parallel execution.
3. **Cache:** Extremely fast onboard memory that stores frequently accessed data.

The CPU relies heavily on the [[Motherboard]] to communicate with [[Random-Access Memory]] and other components.', 14),

(29, 'Random-Access Memory', '**Random-access memory (RAM)** is a form of computer memory that can be read and changed in any order, typically used to store working data and machine code. A random-access memory device allows data items to be read or written in almost the same amount of time irrespective of the physical location of data inside the memory.

## Volatility
Unlike hard drives or solid-state drives, RAM is a volatile memory. This means it requires power to maintain the stored information. If the [[Computer]] loses power, all data stored in RAM is immediately lost.

## Role in Computing
RAM serves as the short-term working space for the [[Central Processing Unit]]. When you open a program or file, the operating system moves it from the slow permanent storage into the much faster RAM, allowing the CPU to access the data almost instantly. 

## Types of RAM
* **SRAM (Static RAM):** Faster, more expensive, used for CPU cache.
* **DRAM (Dynamic RAM):** Slower, cheaper, used for the main system memory. Modern computers typically use DDR SDRAM (Double Data Rate Synchronous Dynamic RAM).', 14),

(30, 'Motherboard', '**A motherboard** (also called mainboard, main circuit board, system board, baseboard, planar board, logic board, or mobo) is the main printed circuit board (PCB) in general-purpose computers and other expandable systems.

## Functionality
It holds and allows communication between many of the crucial electronic components of a system, such as the [[Central Processing Unit]] (CPU) and memory ([[Random-Access Memory]]), and provides connectors for other peripherals. Unlike a backplane, a motherboard usually contains significant sub-systems, such as the central processor, the chipset''s input/output and memory controllers, interface connectors, and other components integrated for general use.

## Key Components on a Motherboard
1. **CPU Socket/Slot:** Where the processor is installed.
2. **Memory Slots:** Where RAM sticks are inserted.
3. **Expansion Slots:** PCIe slots for adding graphics cards, network cards, etc.
4. **Chipset:** Manages data flow between the processor, memory, and peripherals.
5. **Storage Connectors:** SATA or M.2 slots for hard drives and SSDs.

Motherboards dictate the overall capabilities and upgradeability of a computer system.', 14),

(31, 'World Wide Web', '**The World Wide Web (WWW)**, commonly known as the Web, is an information system where documents and other web resources are identified by Uniform Resource Locators (URLs), which may be interlinked by hypertext, and are accessible over the Internet.

## History
The Web was invented by Tim Berners-Lee at CERN in 1989. It opened up the Internet to the general public and fundamentally changed [[Information Technology]] and global communication.

## Core Technologies
The Web is built upon three foundational technologies:
1. **[[HTML]]:** The markup language that structures content.
2. **[[CSS]]:** The style sheet language that determines the visual presentation.
3. **[[JavaScript]]:** The programming language that adds interactivity and logic.

## Web Browsers
Users access the Web via software applications called web browsers (like Chrome, Firefox, or Safari). The browser requests data from a web server using the HTTP protocol, renders the HTML, CSS, and executes the JS to present the user interface. Creating these interfaces is the domain of [[Web Development]].', 15),

(32, 'HTML', '**HyperText Markup Language (HTML)** is the standard markup language for documents designed to be displayed in a web browser. It can be assisted by technologies such as [[CSS]] and scripting languages such as [[JavaScript]].

## Structure and Elements
HTML elements are the building blocks of HTML pages. With HTML constructs, images and other objects such as interactive forms may be embedded into the rendered page. HTML provides a means to create structured documents by denoting structural semantics for text such as headings, paragraphs, lists, links, quotes, and other items.

## HTML Tags
HTML elements are delineated by tags, written using angle brackets. 
* `<p>` denotes a paragraph.
* `<h1>` to `<h6>` denote headings.
* `<a>` denotes a hyperlink (the "HyperText" part of HTML).
* `<img>` is used to embed images.

## Evolution
HTML5 is the current major version of HTML. It introduced semantic elements (like `<article>`, `<footer>`, `<nav>`) and native support for audio and video playback, reducing reliance on third-party plugins in modern [[Web Development]].', 15),

(33, 'CSS', '**Cascading Style Sheets (CSS)** is a style sheet language used for describing the presentation of a document written in a markup language such as [[HTML]] or XML. CSS is a cornerstone technology of the [[World Wide Web]], alongside HTML and [[JavaScript]].

## Separation of Concerns
CSS is designed to enable the separation of presentation and content, including layout, colors, and fonts. This separation can:
* Improve content accessibility.
* Provide more flexibility and control in the specification of presentation characteristics.
* Enable multiple web pages to share formatting by specifying the relevant CSS in a separate `.css` file.
* Reduce complexity and repetition in the structural content.

## The Cascade
The name "Cascading" refers to the specific priority scheme determining which style rule applies if more than one rule matches a particular element. This cascade priority (or specificity) is calculated based on how specific a CSS selector is (e.g., an ID selector overrides a Class selector).

## Responsive Design
Modern CSS is essential for Responsive Web Design, allowing developers to use Media Queries to change the layout of a page depending on the screen size of the device (desktop, tablet, or mobile).', 15),

(34, 'Data Science', '**Data science** is an interdisciplinary field that uses scientific methods, processes, algorithms and systems to extract knowledge and insights from structured and unstructured data. Data science is related to data mining, [[Machine Learning]] and [[Big Data]].

## The Data Science Lifecycle
The typical workflow involves:
1. **Data Collection:** Gathering data from various sources (databases, APIs, web scraping).
2. **Data Cleaning:** Processing the data to handle missing values, outliers, and errors.
3. **Exploratory Data Analysis (EDA):** Visualizing and understanding the characteristics of the data.
4. **Modeling:** Using statistical models or [[Artificial Neural Network]]s to predict outcomes.
5. **Deployment & Communication:** Presenting findings to stakeholders through dashboards or reports.

## Tools of the Trade
Data scientists heavily rely on programming languages. [[Python]] is currently the most popular language in the field, equipped with libraries like Pandas (data manipulation), Matplotlib (visualization), and Scikit-Learn (modeling). SQL is also essential for querying relational databases.', 16),

(35, 'Big Data', '**Big data** is a field that treats ways to analyze, systematically extract information from, or otherwise deal with data sets that are too large or complex to be dealt with by traditional data-processing application software.

## The Three Vs
Big data is traditionally characterized by the "Three Vs":
1. **Volume:** The massive amount of data generated every second.
2. **Velocity:** The speed at which new data is generated and moves around (e.g., social media streams, IoT sensors).
3. **Variety:** The different types of data (structured data in databases, unstructured text, audio, video).

## Infrastructure
Handling Big Data requires specialized [[Information Technology]] infrastructure. Traditional databases are replaced or augmented by distributed storage and processing systems like Apache Hadoop or Apache Spark, often running on large clusters of [[Computer]] servers.

## Value
When properly analyzed using [[Data Mining]] and [[Machine Learning]] techniques, big data can reveal patterns, trends, and associations, especially relating to human behavior and interactions, providing immense value to businesses and researchers.', 16),

(36, 'Data Mining', '**Data mining** is the process of extracting and discovering patterns in large data sets involving methods at the intersection of [[Machine Learning]], statistics, and database systems.

## Purpose and Scope
Data mining is an interdisciplinary subfield of computer science and statistics with an overall goal to extract information (with intelligent methods) from a data set and transform the information into a comprehensible structure for further use. It is a crucial step in the overall [[Data Science]] workflow.

## Common Techniques
* **Anomaly Detection:** Identifying unusual data records that might be interesting or data errors that require further investigation.
* **Association Rule Learning:** Searches for relationships between variables. (e.g., market basket analysis: "If a customer buys bread, they are likely to buy butter").
* **Clustering:** Discovering groups and structures in the data that are in some way or another "similar", without using known structures in the data.
* **Classification:** Generalizing known structure to apply to new data.

Data mining relies heavily on high-performance [[Hardware]] to process vast amounts of [[Big Data]].', 16),

(37, 'Poetry', '**Poetry** is a form of literature that uses aesthetic and often rhythmic qualities of language to evoke meanings in addition to, or in place of, the prosaic ostensible meaning.', 17),
(38, 'Film', '**Film**, also called a movie or a motion picture, is a visual art form used to simulate experiences that communicate ideas, stories, perceptions, feelings, beauty, or atmosphere.', 18),
(39, 'Classical Music', '**Classical music** generally refers to the art music of the Western world, considered to be distinct from Western folk music or popular music traditions.', 19),
(40, 'Painting', '**Painting** is the practice of applying paint, pigment, color or other medium to a solid surface. The medium is commonly applied to the base with a brush.', 20),
(41, 'Ethics', '**Ethics** or moral philosophy is a branch of philosophy that involves systematizing, defending, and recommending concepts of right and wrong behavior.', 21),

(42, 'Roman Empire', '**The Roman Empire** was the post-Republican period of ancient Rome. As a polity, it included large territorial holdings around the Mediterranean Sea in Europe, North Africa, and Western Asia.', 22),
(43, 'Middle Ages', 'In the history of Europe, the **Middle Ages** or medieval period lasted approximately from the 5th to the late 15th centuries. It began with the fall of the Western [[Roman Empire]].', 23),
(44, 'Industrial Revolution', '**The Industrial Revolution** was the transition to new manufacturing processes in Great Britain, continental Europe, and the United States, that occurred during the period from around 1760 to about 1820-1840.', 24),
(45, 'World War II', '**World War II** was a global conflict that lasted from 1939 to 1945. The vast majority of the world''s countries fought as part of two opposing military alliances: the Allies and the Axis.', 25),
(46, 'Information Age', '**The Information Age** is a historical period that began in the mid-20th century, characterized by a rapid epochal shift from the traditional industry established by the [[Industrial Revolution]] to an economy primarily based upon [[Information Technology]].', 26);

INSERT INTO article_tags (article_id, tag_id) VALUES
(4, 7), (5, 7), (5, 4), (6, 7), (6, 9),
(19, 1), (19, 6), (19, 9), (20, 1), (20, 5), (20, 9), (21, 1), (21, 9),
(22, 2), (22, 6), (23, 2), (24, 2), (24, 1),
(25, 3), (25, 8), (26, 3), (27, 3), (27, 9),
(28, 4), (29, 4), (30, 4),
(31, 5), (31, 8), (32, 5), (32, 1), (33, 5), (33, 1),
(34, 6), (34, 1), (35, 6), (35, 7), (36, 6), (36, 2);

*/