from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

# 🔥 GPU CHECK
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"\n🔥 USING DEVICE: {device}\n")

model = model.to(device)


def generate_response(prompt):

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True
    )

    # 🔥 move tensors to GPU
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():

        outputs = model.generate(
            **inputs,
            max_new_tokens=50,
            do_sample=False
        )

    result = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return result