# Game of Thrones Conversational Assistant

This project is a small conversational assistant about the Game of Thrones universe.

The assistant combines two sources of information:

- a corpus of character documents used with Retrieval-Augmented Generation;
- a Knowledge Graph containing relationships between characters.

## Main Features

- document retrieval using embeddings and FAISS;
- character relationships stored in GraphDB;
- SPARQL queries to retrieve structured facts;
- answer generation using a language model;
- basic adversarial testing with prompt injection and jailbreak attempts.

## Goal

The goal of this project is not to build a production-ready assistant, but to demonstrate the integration of document retrieval, a Knowledge Graph, SPARQL queries, and a language model in a complete working prototype.