cd `dirname $0`/../src

LLM=examples.llm_schema
#MODEL=../local/models/mlx/Mistral-7B-v0.2-Instruct-f16
#MODEL=./mistral/mlx_model_q4
#MODEL=mistralai/Mistral-7B-Instruct-v0.2
MODEL=mlx-community/Mistral-7B-v0.2-4bit
OPTIONS="--max-tokens 1000 --repeat-prompt --temp 0.8"

PROMPT='[INST] Parse the following address into a JSON object: "27 Barrow St, New York, NY 10014". Your answer should be only a JSON object according to this schema: {"type": "object", "properties": {"streetNumber": {"type": "number"}, "streetName": {"type": "string"}, "city": {"type": {"string"}}, "state": {"type": "string"}, "zipCode": {"type": "number"}}}. Do not explain the result, just output it. Do not add any additional information. [/INST]'

if [ "$1" == "--mixtral" ]; then
  shift
  MODEL=./mixtral/mlx_model_q4
  #MODEL=./mixtral/mlx_model_q8
  #MODEL=./mixtral/mlx_model_f16
  MODEL_TYPE="--model-type mixtral"
fi
if [ "$1" == "--encapsulated" ]; then
  shift
  PROMPT='[INST] Your mission is to parse the following address into a JSON object: "27 Barrow St, New York, NY 10014". Your answer should be only a JSON object according to this schema: {"type": "object", "properties": {"streetNumber": {"type": "number"}, "streetName": {"type": "string"}, "city": {"type": {"string"}}, "state": {"type": "string"}, "zipCode": {"type": "number"}}}.
First, think through the mission, and then output a JSON object wrapped between the lines ```json and ```. [/INST]'
fi

if [ "$1" == "--no-schema" ]; then
  shift
  python3 -m $LLM --model-path $MODEL $MODEL_TYPE $OPTIONS --prompt "$PROMPT" $@
else
  SCHEMA='{"type": "object", "properties": {"streetNumber": {"type": "number"}, "streetName": {"type": "string"}, "city": {"type": "string"}, "state": {"type": "string"}, "zipCode": {"type": "number"}}}'
  python3 -m $LLM --model-path $MODEL $MODEL_TYPE $OPTIONS --prompt "$PROMPT" --schema "$SCHEMA" $ENCAPSULATED $@
fi
