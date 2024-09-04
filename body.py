import cv2
import mediapipe as mp
import numpy as np
import math

def find_closest_array(target_array, arrays):
    """
    특정 배열의 값들과 비교하여 가장 가까운 값이 많이 존재하는 배열을 반환하는 함수.

    :param target_array: 비교 대상이 되는 특정 배열
    :param arrays: 비교할 3개의 배열이 포함된 리스트
    :return: 특정 배열의 값들과 가장 가까운 값이 많이 존재하는 배열
    """
    closest_counts = [0] * len(arrays)
    
    for value in target_array:
        # 각 value에 대해 모든 배열에서 가장 가까운 값 찾기
        closest_distances = [min(abs(value - arr_value) for arr_value in array) for array in arrays]
        closest_index = closest_distances.index(min(closest_distances))
        closest_counts[closest_index] += 1
    
    # 가장 많은 가까운 값이 있는 배열의 인덱스 찾기
    best_match_index = closest_counts.index(max(closest_counts))
    return best_match_index

#신체 요소 길이 측정
factor = np.zeros(10) 

# Mediapipe 솔루션 초기화
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# 이미지 파일 경로
IMAGE_FILE = 'image.jpg'
#cap = cv2.VideoCapture(0)

# Mediapipe Pose 설정
with mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        enable_segmentation=True,
        min_detection_confidence=0.5) as pose:
    
    # 이미지 읽기
    image = cv2.imread(IMAGE_FILE)
    
    # 이미지가 제대로 불러와졌는지 확인
    if image is None:
        print(f"이미지 파일을 불러오는데 실패했습니다: {IMAGE_FILE}")
    else:
        image_height, image_width, _ = image.shape
        
        # 처리 전 BGR 이미지를 RGB로 변환합니다.
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        
        coords_list = []
        # 포즈 랜드마크가 감지되었는지 확인합니다.
        if results.pose_landmarks:
            # 각 특징점의 좌표를 출력합니다.
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                x = landmark.x * image_width
                y = landmark.y * image_height
                coords = (x, y)
                coords_list.append(coords)
                
                #print(f"Landmark {idx}: (x: {x}, y: {y})")
            location = np.array(coords_list)
            
            # 이미지 위에 포즈 랜드마크를 그립니다.
            annotated_image = image.copy()
            mp_drawing.draw_landmarks(
                annotated_image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            
            # 세그멘테이션 마스크 얻기
            mask = results.segmentation_mask
            mask = np.where(mask > 0.1, 1, 0).astype(np.uint8)  # Thresholding for better segmentation
            person_segment = cv2.bitwise_and(image, image, mask=mask)
        
            #좌표 신체 요소로 추출
            factor[1] = location[29][1] - location[11][1] #어깨높이
            
            under_x = abs(location[15][0] - location[13][0])**2
            under_y = abs(location[13][1] - location[15][1])**2
            factor[3] = math.sqrt(under_x + under_y) #아래팔길이
            
            shoulder_x = (location[11][0] - location[12][0])**2
            shoulder_y = abs(location[11][1] - location[12][1])**2
            factor[5] = math.sqrt(shoulder_x + shoulder_y)#어깨 너비
            
            up_x = abs(location[13][0] - location[11][0])**2
            up_y = abs(location[11][1] - location[13][1])**2
            factor[6] = math.sqrt(up_x + up_y) #위팔길이

            #총길이
            #사진 흑백으로 전환
            gray = cv2.cvtColor(person_segment, cv2.COLOR_BGR2GRAY)
            # 이진화 (Thresholding)
            _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            # 윤곽선 찾기
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # 윤곽선 중 가장 높은 y좌표 찾기
            highest_point = None
            for contour in contours:
                for point in contour:
                    if (highest_point is None or point[0][1] < highest_point[1]) and point[0][1] != 0:
                        highest_point = tuple(point[0])
            
             # Haar Cascade 얼굴 검출기 초기화
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            # 흑백 이미지로 변환 (얼굴 검출기는 흑백 이미지를 요구합니다)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # 얼굴 검출
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            for (x, y, w, h) in faces:
                cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # 턱 좌표 계산 (간단히 얼굴 영역의 가장 아래 점으로 가정)
                jaw_x = x + w // 2
                jaw_y = y + h
                factor[2] = jaw_y - highest_point[1]
                # 턱 좌표에 빨간색 점 그리기
                cv2.circle(image, (jaw_x, jaw_y), 5, (0, 0, 255), -1)

            #총길이
            factor[7] = location[29][1] - highest_point[1]
            
            #비율 
            height = float(input("키를 입력하세요: "))
            rat = height / factor[7]

            #샅높이
            leg = location[29][1] - location[22][1]
            body_len = location[23][1] - location[11][1] + 13 / rat # 몸통수직길이(조정치 필요)
            print(leg * rat, body_len * rat)
            factor[4] = leg - body_len
            #머리길이
            #factor[2] = round(jaw_y - highest_point[1])
            
            for i in range(1, 8):
                factor[i] = round(factor[i] * rat, 1)
            
            print("어깨높이: ", factor[1])
            print("머리 길이: ", factor[2])
            print("아래팔길이: ", factor[3])
            print("샅높이 - 몸통수직길이: ", factor[4])
            print("어깨너비: ", factor[5])
            print("위팔길이: ", factor[6])
            print("키: ", factor[7])
            
            # 결과 이미지를 화면에 표시합니다.
            '''cv2.imshow('Annotated Image', annotated_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()'''
            
            #체형 별 측정값
            body_tri = [0, 128.3, 22.4, 24.8, 8.3, 36.5, 31.3, 0]
            body_intri = [0, 129.5, 22.1, 24.2, 8, 36.9, 30.7, 0]
            body_rec = [0, 130.9, 22.1, 24.7, 7.8, 35.2, 30.7, 0]     
            body = [body_tri, body_intri, body_rec]
            
            idx = find_closest_array(factor, body)
            if idx == 0:
                print("삼각형 체형")       
            elif idx == 1:
                print("역삼각형 체형")
            elif idx == 2:
                print("사각형 체형")
                
            
            
            
            
            
            
            
            
            
            