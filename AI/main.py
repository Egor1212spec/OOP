
import os
import json
import re
import pymorphy3
from catboost import CatBoostClassifier, Pool


class EGESolver:

    def __init__(self, model_path="best_model_catboost"):
        self.model_path = model_path
        self.morph = pymorphy3.MorphAnalyzer()
        self.model = None
        self.reverse_label_map = None
        self._load_model()
        
    def _load_model(self):
        model_file = os.path.join(self.model_path, "catboost_model.cbm")
        label_file = os.path.join(self.model_path, "label_map.json")
        
        self.model = CatBoostClassifier()
        self.model.load_model(model_file)
        
        if os.path.exists(label_file):
            with open(label_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.reverse_label_map = {int(k): v for k, v in data.get('reverse_label_map', {}).items()}
        else:
            self.reverse_label_map = {i: i + 1 for i in range(27)}
    
    def _preprocess(self, text):
        text_clean = re.sub(r'[^\w\s]', '', text).lower()
        return " ".join([self.morph.parse(w)[0].normal_form for w in text_clean.split()])
    
    def classify(self, text):
        lemma_text = self._preprocess(text)
        pool = Pool(data=[[lemma_text]], text_features=[0])
        pred_class = int(self.model.predict(pool)[0])
        probs = self.model.predict_proba(pool)[0]
        task_number = self.reverse_label_map.get(pred_class, pred_class + 1)
        confidence = probs[pred_class]
        return {"task_number": task_number, "confidence": float(confidence)}
    
    def solve(self, text):
        result = self.classify(text)
        task_number = result["task_number"]
        solver_method = getattr(self, f"_solve_{task_number}", None)
        if solver_method:
            answer = solver_method(text)
        else:
            answer = f"Солвер {task_number} не найден"
        return {"task_number": task_number, "confidence": result["confidence"], "answer": answer}
    
    def _solve_1(self, text): print("Вызван солвер 1"); return None
    def _solve_2(self, text): print("Вызван солвер 2"); return None
    def _solve_3(self, text): print("Вызван солвер 3"); return None
    def _solve_4(self, text): print("Вызван солвер 4"); return None
    def _solve_5(self, text): print("Вызван солвер 5"); return None
    def _solve_6(self, text): print("Вызван солвер 6"); return None
    def _solve_7(self, text): print("Вызван солвер 7"); return None
    def _solve_8(self, text): print("Вызван солвер 8"); return None
    def _solve_9(self, text): print("Вызван солвер 9"); return None
    def _solve_10(self, text): print("Вызван солвер 10"); return None
    def _solve_11(self, text): print("Вызван солвер 11"); return None
    def _solve_12(self, text): print("Вызван солвер 12"); return None
    def _solve_13(self, text): print("Вызван солвер 13"); return None
    def _solve_14(self, text): print("Вызван солвер 14"); return None
    def _solve_15(self, text): print("Вызван солвер 15"); return None
    def _solve_16(self, text): print("Вызван солвер 16"); return None
    def _solve_17(self, text): print("Вызван солвер 17"); return None
    def _solve_18(self, text): print("Вызван солвер 18"); return None
    def _solve_19(self, text): print("Вызван солвер 19"); return None
    def _solve_20(self, text): print("Вызван солвер 20"); return None
    def _solve_21(self, text): print("Вызван солвер 21"); return None
    def _solve_22(self, text): print("Вызван солвер 22"); return None
    def _solve_23(self, text): print("Вызван солвер 23"); return None
    def _solve_24(self, text): print("Вызван солвер 24"); return None
    def _solve_25(self, text): print("Вызван солвер 25"); return None
    def _solve_26(self, text): print("Вызван солвер 26"); return None
    def _solve_27(self, text): print("Вызван солвер 27"); return None


if __name__ == "__main__":
    solver = EGESolver("best_model_catboost")
    
    test_texts = [
        "На рисунке справа можно видеть схему дорог С-ского города изображенную в виде графа, а в таблице слева содержатся сведения о длинах этих дорог (в километрах). Нумерация достопримечательностей города в таблице никак не связана с буквенными обозначениями на графе, но известно, что длина дороги из D в B больше длины дороги из D в C. Проложите самый длинный маршрут для экскурсии из пункта G в пункт E, если через каждую дорогу можно пройти лишь единожды. Укажите в ответе длину такого маршрута"
    ]
    
    for text in test_texts:
        result = solver.solve(text)
        print(f"Задание: {result['task_number']}, Уверенность: {result['confidence']:.2%}")
        print()
