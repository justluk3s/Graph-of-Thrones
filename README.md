# Game of Thrones Conversational Assistant

This project implements a conversational assistant for the Game of Thrones universe by combining Retrieval-Augmented Generation (RAG) with a Knowledge Graph.

## Domain

This project explores the **Game of Thrones** universe using the [public datasets created by Jeffrey Lancaster](https://github.com/jeffreylancaster/game-of-thrones). The original project combines multiple complementary datasets describing characters, relationships, episodes, scenes, locations, and other narrative information collected from the HBO television series.

We selected this domain because it naturally provides both structured and unstructured knowledge. This makes it particularly suitable for studying how Retrieval-Augmented Generation (RAG) and Knowledge Graphs can be integrated into a single conversational assistant.

For this project we use:

- **A document corpus**, containing textual information about characters obtained from public Game of Thrones datasets and APIs, which serves as the unstructured knowledge source for retrieval.
- **A Knowledge Graph**, extracted from the dataset's explicit character relationships, representing facts such as family ties, alliances, service relationships, and kills.

The document corpus and the Knowledge Graph are intentionally complementary. The corpus provides descriptive information about characters, while the Knowledge Graph captures explicit semantic relationships that can be queried precisely through SPARQL and incorporated into the language model's context.

## Project Objective

The objective of this project is to build a conversational assistant capable of answering questions about the Game of Thrones universe by combining semantic retrieval with structured reasoning.

Given a user's question, the system retrieves relevant character information from the document corpus and complementary facts from the Knowledge Graph. Both sources are then provided to a language model, allowing it to generate responses that combine descriptive information with explicit structured relationships.

## System Components

- semantic document retrieval using embeddings and FAISS;
- Knowledge Graph stored in GraphDB;
- SPARQL queries for structured fact retrieval;
- answer generation using a language model;
- basic adversarial evaluation through prompt injection and jailbreak tests.

## Goal

The goal of this project is to demonstrate how Retrieval-Augmented Generation and Knowledge Graphs can be effectively integrated into a single conversational assistant. The focus is on building a functional prototype that highlights the complementary strengths of semantic retrieval and structured knowledge.



## Project Structure
```
graph-of-thrones/
├── data/
│   ├── characters.json
│   └── kg.trig
├── scripts/
│   └── ...
├── src/
│   ├── graphdb_client.py
│   └── ...
├── pyproject.toml
├── README.md
├── .gitignore
└── .env.example
```

## Knowledge Graph

The Knowledge Graph is stored in GraphDB using RDF/TriG.

It contains structured character-to-character relationships such as:

- parentOf
- childOf
- siblingOf
- killed
- killedBy
- serves
- servedBy
- marriedOrEngagedTo

The graph is stored in GraphDB as RDF/TriG and queried through SPARQL to retrieve structured facts that are incorporated into the language model context.



## GraphDB Client

The GraphDB client is implemented in `src/graphdb_client.py`.

It is responsible for:
- connecting to GraphDB;
- executing SPARQL queries;
- retrieving incoming and outgoing character relationships;
- formatting retrieved Knowledge Graph facts into contextual information that can be injected into the language model prompt.
