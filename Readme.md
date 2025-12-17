# Ontology-Based Intelligent Tutoring System (ITS)
## Area of Geometric Shapes

## 📌 Project Overview
This project implements an **Ontology-Based Intelligent Tutoring System (ITS)** for learning the **area calculation of geometric shapes**.  
The system integrates **Semantic Web technologies (OWL ontology)** with a **Python-based graphical user interface (GUI)** to provide adaptive learning, multiple questions, and performance-based feedback.

The tutoring system supports multiple geometric shapes and skill levels, enabling personalized and interactive learning experiences.

---

## 🎯 Objectives
- To design an ontology that models geometric shapes, questions, skill levels, hints, and formulas
- To develop an interactive GUI for learner interaction
- To provide adaptive question selection based on shape and skill level
- To deliver immediate and performance-based feedback
- To ensure ontology consistency using a reasoner

---

## 🧠 System Architecture
The system consists of two main components:

1. **Ontology Layer**
   - Developed using **Protégé**
   - Modeled in **OWL (Web Ontology Language)**
   - Stores domain knowledge such as shapes, questions, formulas, hints, and skill levels

2. **Application Layer**
   - Developed using **Python**
   - GUI implemented using **Tkinter**
   - Ontology accessed using **Owlready2**

---

## 📘 Ontology Design

### Main Classes
- `Shape` (Rectangle, Circle, Triangle, Square)
- `Question`
- `Formula`
- `Hint`
- `SkillLevel` (Beginner, Intermediate, Advanced)
- `Topic`

### Object Properties
- `hasShape` – links Question to Shape
- `hasSkillLevel` – links Question to SkillLevel
- `hasHint` – links Question to Hint
- `usesFormula` – links Question to Formula
- `hasTopic` – links Question to Topic

### Data Properties
- `hasText` – stores question, hint, and formula text
- `hasCorrectAnswer` – stores correct answers
- `hasName` – stores human-readable names

### Reasoning
- **HermiT Reasoner** is used in Protégé
- Ensures logical consistency and datatype correctness

---

## 🖥️ Graphical User Interface (GUI)

The GUI acts as the interaction layer between the learner and the ontology.

### Key Features
- Shape selection (Rectangle, Circle, Triangle, Square)
- Skill level selection (Beginner, Intermediate, Advanced)
- Multiple questions per shape and skill level
- Question navigation using "Next" button
- Answer submission and evaluation
- Hint and formula support
- Attempt tracking per question
- Final performance-based feedback

The interface is designed with simplicity and clarity to enhance user experience.

---

## ⚙️ Technologies Used
- **Python 3.x**
- **Tkinter** (GUI development)
- **Protégé** (Ontology development)
- **OWL (Web Ontology Language)**
- **Owlready2** (Ontology integration in Python)
- **HermiT Reasoner**

---

## 📂 Project Structure
