#to add more fields
connectorSchema = {
  "properties": {
    "name": {
      "type": "string"
    },
    "config": {
      "type": "object",
      "properties": {
        "connector.class": {
          "type": "string"
        },
        "tasks.max": {
          "type": "string"
        },
        "topics": {
          "type": "string"
        },
      },
      "required": [
        "connector.class",
        "topics",
      ]
    }
  },
  "required": [
    "name",
    "config"
  ]
}
