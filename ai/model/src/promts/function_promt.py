query_hotels = {
                "name": "query_hotels",
                "description": "Query hotels based on text input (returns top 5 results)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for hotels"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of hotels to return (limited to 5)",
                            "default": 5,
                            "maximum": 5
                        }
                    },
                    "required": ["query_text"]
                }
            }
query_places = {
                "name": "query_places",
                "description": "Query places based on text input (returns top 20 results)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for places"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of places to return (limited to 20)",
                            "default": 20,
                            "maximum": 20
                        }
                    },
                    "required": ["query_text"]
                }
            }
query_fnb = {
                "name": "query_fnb",
                "description": "Query FnB based on text input (returns top 20 results)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_text": {
                            "type": "string",
                            "description": "The query text to search for FnB"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of FnB to return (limited to 20)",
                            "default": 20,
                            "maximum": 20
                        }
                    },
                    "required": ["query_text"]
                }
            }
search_by_price_range = {
                "name": "search_by_price_range",
                "description": "Search within a specific price range",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_price": {
                            "type": "number",
                            "description": "Minimum price for search"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Maximum price for search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["min_price", "max_price"]
                }
            }
search_by_rating = {
                "name": "search_by_rating",
                "description": "Search with minimum rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_rating": {
                            "type": "number",
                            "description": "Minimum rating for search"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["min_rating"]
                }
            }
search_by_category = {
                "name": "search_by_category",
                "description": "Search by category",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["category"]
                }
            }
search_by_location = {
                "name": "search_by_location",
                "description": "Search places by location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["location"]
                }
            }
search_by_menu_item = {
                "name": "search_by_menu_item",
                "description": "Search FnB by menu item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_name": {
                            "type": "string",
                            "description": "Menu item to search for"
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return",
                            "default": 5
                        }
                    },
                    "required": ["item_name"]
                }
            }