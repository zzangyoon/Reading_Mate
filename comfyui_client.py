"""
ComfyUI API 클라이언트
- Flux 모델 전용 이미지 생성
- Storybook LoRA 적용 
"""
# uv run comfy launch
# uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8003

import requests
import json
import time
import uuid
from typing import Dict
from PIL import Image
from pathlib import Path


class ComfyUIClient:
    def __init__(self, server_address: str = "100.100.53.32:8288"):
        """
        ComfyUI 클라이언트 초기화
        
        Args:
            server_address: ComfyUI 서버 주소 (IP:PORT)
        """
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
    
    def generate_image(self, prompt_data: Dict) -> Dict:
        """
        이미지 생성
        
        Args:
            prompt_data: 프롬프트 및 파라미터 딕셔너리
            
        Returns:
            생성 결과 (image_path, quality_score 등)
        """
        print("🎨 이미지 생성 시작")
        
        # Flux 워크플로우 생성
        workflow = self._get_flux_workflow()
        
        # 프롬프트 주입
        workflow = self._inject_prompt(workflow, prompt_data)
        
        # ComfyUI에 요청
        try:
            prompt_id = self._queue_prompt(workflow)
            print(f"✅ Prompt ID: {prompt_id}")
            
            # 완료 대기
            result = self._wait_for_completion(prompt_id)
            
            # 이미지 다운로드
            image_path = self._download_image(result)
            
            # 품질 평가
            quality_score = self._evaluate_image_quality(image_path)
            
            return {
                "image_path": image_path,
                "prompt_id": prompt_id,
                "quality_score": quality_score,
                "generation_time": 30.0
            }
            
        except Exception as e:
            print(f"❌ 오류 발생: {type(e).__name__} - {str(e)}")
            raise
    
    def _get_flux_workflow(self) -> Dict:
        """
        Flux 모델용 기본 워크플로우 반환
        
        워크플로우 구성:
        - UNETLoader: Flux 모델
        - LoraLoader: Storybook LoRA
        - DualCLIPLoader: CLIP 모델
        - KSampler: 샘플링 (Euler, 20 steps, CFG 1.0)
        - VAEDecode: 이미지 디코딩
        """
        return {
            "18": {
                "class_type": "UNETLoader",
                "inputs": {
                    "unet_name": "flux1-krea-dev_fp8_scaled.safetensors",
                    "weight_dtype": "default"
                }
            },
            "2": {
                "class_type": "LoraLoaderModelOnly",
                "inputs": {
                    "lora_name": "pp-storybook_rank2_bf16.safetensors",
                    "strength_model": 0.8,
                    "model": ["18", 0]
                }
            },
            "13": {
                "class_type": "DualCLIPLoader",
                "inputs": {
                    "clip_name1": "clip_l.safetensors",
                    "clip_name2": "t5xxl_fp16.safetensors",
                    "type": "flux"
                }
            },
            "4": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": "",
                    "clip": ["13", 0]
                }
            },
            "16": {
                "class_type": "ConditioningZeroOut",
                "inputs": {
                    "conditioning": ["4", 0]
                }
            },
            "10": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                }
            },
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "seed": 0,
                    "steps": 20,
                    "cfg": 1.0,
                    "sampler_name": "euler",
                    "scheduler": "simple",
                    "denoise": 1.0,
                    "model": ["2", 0],
                    "positive": ["4", 0],
                    "negative": ["16", 0],
                    "latent_image": ["10", 0]
                }
            },
            "14": {
                "class_type": "VAELoader",
                "inputs": {
                    "vae_name": "ae.safetensors"
                }
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["14", 0]
                }
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["6", 0]
                }
            }
        }
    
    def _inject_prompt(self, workflow: Dict, prompt_data: Dict) -> Dict:
        """
        워크플로우에 프롬프트 및 파라미터 주입
        
        Args:
            workflow: 워크플로우 딕셔너리
            prompt_data: 프롬프트 데이터
            
        Returns:
            업데이트된 워크플로우
        """
        positive_prompt = prompt_data.get("positive", "")
        style_params = prompt_data.get("style_params", {})
        
        # 파라미터 추출
        steps = style_params.get("steps", 20)
        cfg = style_params.get("cfg_scale", 1.0)
        sampler = style_params.get("sampler", "euler")
        width = style_params.get("width", 1024)
        height = style_params.get("height", 1024)
        lora_strength = style_params.get("lora_strength", 0.8)
        
        print(f"✨ Positive: {positive_prompt[:100]}...")
        print(f"⚙️ Size: {width}x{height}, Steps: {steps}, CFG: {cfg}, LoRA: {lora_strength}")
        
        # 워크플로우 업데이트
        for node_id, node in workflow.items():
            if not isinstance(node, dict):
                continue
                
            class_type = node.get("class_type", "")
            
            # 이미지 크기
            if class_type == "EmptyLatentImage":
                node["inputs"]["width"] = int(width)
                node["inputs"]["height"] = int(height)
            
            # LoRA 강도
            elif class_type == "LoraLoaderModelOnly":
                node["inputs"]["strength_model"] = float(lora_strength)
            
            # 샘플링 파라미터
            elif class_type == "KSampler":
                node["inputs"]["seed"] = int(time.time() * 1000) % (2**32)
                node["inputs"]["steps"] = int(steps)
                node["inputs"]["cfg"] = float(cfg)
                node["inputs"]["sampler_name"] = sampler
            
            # Positive 프롬프트
            elif class_type == "CLIPTextEncode" and node_id == "4":
                node["inputs"]["text"] = positive_prompt
        
        return workflow
    
    def _queue_prompt(self, workflow: Dict) -> str:
        """ComfyUI 큐에 프롬프트 제출"""
        url = f"http://{self.server_address}/prompt"
        payload = {"prompt": workflow, "client_id": self.client_id}
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()["prompt_id"]
    
    def _wait_for_completion(self, prompt_id: str, timeout: int = 300) -> Dict:
        """이미지 생성 완료 대기"""
        print("⏳ 이미지 생성 대기 중...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"http://{self.server_address}/history/{prompt_id}"
                )
                if response.status_code == 200:
                    history = response.json()
                    if prompt_id in history:
                        print("✅ 생성 완료!")
                        return history[prompt_id]
            except:
                pass
            
            time.sleep(2)
        
        raise TimeoutError("이미지 생성 시간 초과")
    
    def _download_image(self, result: Dict) -> str:
        """생성된 이미지 다운로드"""
        outputs = result.get("outputs", {})
        
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                image_info = node_output["images"][0]
                filename = image_info["filename"]
                subfolder = image_info.get("subfolder", "")
                file_type = image_info.get("type", "output")
                
                # 이미지 다운로드
                url = f"http://{self.server_address}/view"
                params = {
                    "filename": filename,
                    "subfolder": subfolder,
                    "type": file_type
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                # 저장
                Path("generated_images").mkdir(exist_ok=True)
                output_path = f"generated_images/{filename}"
                
                with open(output_path, "wb") as f:
                    f.write(response.content)
                
                print(f"💾 저장 완료: {output_path}")
                return output_path
        
        raise ValueError("생성된 이미지를 찾을 수 없습니다")
    
    def _evaluate_image_quality(self, image_path: str) -> float:
        """
        이미지 품질 평가 (간단한 휴리스틱)
        
        - 해상도 기반 점수
        - 파일 크기 기반 점수
        """
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            # 해상도 점수
            resolution_score = min(1.0, (width * height) / (1024 * 1024))
            
            # 파일 크기 점수
            import os
            file_size = os.path.getsize(image_path)
            size_score = min(1.0, file_size / (100 * 1024))
            
            return (resolution_score + size_score) / 2
            
        except Exception as e:
            print(f"⚠️ 품질 평가 오류: {e}")
            return 0.5
        
        # uv run comfy launch