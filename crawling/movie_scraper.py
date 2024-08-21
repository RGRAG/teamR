from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import time
import streamlit as st

# Streamlit 제목
st.title("영화 정보 크롤링")

# 크롬 드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Chrome(options=options)

# 크롤링할 URL
base_url = 'https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&qvt=0&query=%ED%98%84%EC%9E%AC%EC%83%81%EC%98%81%EC%98%81%ED%99%94'
driver.get(base_url)
time.sleep(2)  # 페이지 로딩 대기

# 모든 영화의 상세 페이지 URL을 저장할 배열
movie_urls = []

# 페이지네이션 처리 (영화 목록 URL 수집)
for page in range(1, 2):  # 8페이지까지 크롤링
    print(f"Processing page {page}")
    time.sleep(2)  # 페이지 로딩 대기
    
    # 페이지 소스 확인
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # 영화 정보를 담고 있는 요소 선택
    cards = soup.select('.card_content .card_item')

    for card in cards:
        title = card.select_one('.title .this_text').text.strip() if card.select_one('.title .this_text') else 'N/A'
        detail_link_suffix = card.select_one('.title .this_text').get('href') if card.select_one('.title .this_text') else None
        detail_link = f'https://search.naver.com/search.naver{detail_link_suffix}' if detail_link_suffix else None
        if detail_link:
            movie_urls.append(detail_link)

    # 페이지 넘버에 따라 다음 페이지로 이동
    try:
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.pg_next.on'))
        )
        next_button.click()
        time.sleep(2)  # 페이지 이동 대기
    except TimeoutException:
        print("다음 페이지 버튼을 찾을 수 없습니다.")
        break

# 모든 영화 URL을 수집한 후, 각 URL에 대해 상세 정보 크롤링
movies = []

for detail_link in movie_urls:
    print(f"Navigating to detail page: {detail_link}")
    driver.get(detail_link)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.tab_list')))
    except TimeoutException:
        print("Detail page did not load correctly.")
        continue

    detail_soup = BeautifulSoup(driver.page_source, 'html.parser')

    # 탭 링크들 가져오기

    tabs = detail_soup.select('.tab_list .tab a')
    tab_urls = {tab.text.strip(): f"https://search.naver.com/search.naver{tab['href']}" for tab in tabs}
    print(f"tab url", tab_urls)


            # 기본정보 탭에서 정보 추출
    if '기본정보' in tab_urls:
        basic_info_url = tab_urls['기본정보']
        driver.get(basic_info_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.detail_info')))
        basic_info_soup = BeautifulSoup(driver.page_source, 'html.parser')

        poster_img_element = basic_info_soup.select_one('.detail_info .thumb._item img')
        poster_url = poster_img_element['src'] if poster_img_element else 'N/A'

        release_date = basic_info_soup.select_one('.info_group dd').text.strip() if basic_info_soup.select_one('.info_group dd') else 'N/A'
        rating = basic_info_soup.select_one('.info_group:nth-of-type(2) dd').text.strip() if basic_info_soup.select_one('.info_group:nth-of-type(2) dd') else 'N/A'
        genre = basic_info_soup.select_one('.info_group:nth-of-type(3) dd').text.strip() if basic_info_soup.select_one('.info_group:nth-of-type(3) dd') else 'N/A'
        country = basic_info_soup.select_one('.info_group:nth-of-type(4) dd').text.strip() if basic_info_soup.select_one('.info_group:nth-of-type(4) dd') else 'N/A'
        running_time = basic_info_soup.select_one('.info_group:nth-of-type(5) dd').text.strip() if basic_info_soup.select_one('.info_group:nth-of-type(5) dd') else 'N/A'
        distributor = basic_info_soup.select_one('.info_group:nth-of-type(6) dd').text.strip() if basic_info_soup.select_one('.info_group:nth-of-type(6) dd') else 'N/A'

        description_element = basic_info_soup.select_one('.text._content_text')
        description = description_element.text.strip() if description_element else 'N/A'
    else:
        poster_url = release_date = rating = genre = country = running_time = distributor = description = 'N/A'

    # 감독/출연 탭에서 정보 추출
    if '감독/출연' in tab_urls:
        print("---------------------------")
        print("감독 section")
        print("---------------------------")
        driver.get(tab_urls['감독/출연'])
        # try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.info_group')))
        # except TimeoutException:
        #     print("Element '.info_group' not found. Skipping to the next movie.")
        #     continue  # 다음 영화로 넘어감
        # 감독 정보가 있는 섹션 추출
        # 감독 정보가 있는 섹션 추출
        director_section = detail_soup.select('.cast_list li')

        directors = []
        for section in director_section:
            # 역할이 '감독'인 경우에만 추출
            print(section)
            role = section.select_one('.sub_text ._text').text.strip() if section.select_one('.sub_text ._text') else 'N/A'
            print(role)
            director_name = section.select_one('.name ._text').text.strip() if section.select_one('.name ._text') else 'N/A'

            print("---------------------------")
            print(director_name)
            print("---------------------------")
            
            if role == '감독':
                # 감독 이름 추출
                director_name = section.select_one('.name ._text').text.strip() if section.select_one('.name ._text') else 'N/A'
                
                # 썸네일 이미지 URL 추출
                thumbnail_url = section.select_one('.thumb img')['src'] if section.select_one('.thumb img') else 'N/A'
                
                # 감독 정보 저장
                directors.append({
                    'name': director_name,
                    'thumbnail_url': thumbnail_url
                })

        # 추출된 감독 정보 출력 (테스트용)
        for director in directors:
            print(f"Director Name: {director['name']}")
            print(f"Thumbnail URL: {director['thumbnail_url']}")
            print("---")
        # 감독 정보가 있는지 확인
        # if director_section:
        #     director_name = director_section.select_one('.cast_list .name ._text').text.strip() if director_section.select_one('.cast_list .name ._text') else 'N/A'
        #     director_role = director_section.select_one('.cast_list .sub_text ._text').text.strip() if director_section.select_one('.cast_list .sub_text ._text') else 'N/A'
        # else:
        #     director_name = 'N/A'
        #     director_role = 'N/A'

        # 주연 배우 정보 추출
        # actors_section = detail_soup.select_one('.cast_box:has(h3.title_numbering:contains("주연"))')



        # 주연 배우 정보가 있는지 확인
        # actors = []
        # if actors_section:
        #     actor_elements = actors_section.select('.cast_list .name ._text')
        #     for actor_element in actor_elements:
        #         actor_name = actor_element.text.strip()
        #         actors.append(actor_name)

        # print(actors)

    else:
        director = actors = 'N/A'

    # 관람평 탭에서 정보 추출
    if '관람평' in tab_urls:
        driver.get(tab_urls['관람평'])
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.scroll_box')))
        rating_soup = BeautifulSoup(driver.page_source, 'html.parser')
        # 실관람객 평점 추출
        rating_section = detail_soup.select_one('.lego_rating_box_see')
        if rating_section:
            real_rating = rating_section.select_one('.area_star_number').text.strip() if rating_section.select_one('.area_star_number') else 'N/A'
            rating_participants = rating_section.select_one('.area_people').text.strip() if rating_section.select_one('.area_people') else 'N/A'
            
            male_rating = rating_section.select_one('.area_card_male .this_text').text.strip() if rating_section.select_one('.area_card_male .this_text') else 'N/A'
            female_rating = rating_section.select_one('.area_card_female .this_text').text.strip() if rating_section.select_one('.area_card_female .this_text') else 'N/A'
        else:
            real_rating = rating_participants = male_rating = female_rating = 'N/A'

        print(f"Real Rating: {real_rating}")
        print(f"Participants: {rating_participants}")
        print(f"Male Rating: {male_rating}")
        print(f"Female Rating: {female_rating}")

        # 점수별 비율 추출
        score_distribution = {}
        score_distribution_section = detail_soup.select_one('.lego_rating_box_change_score')
        if score_distribution_section:
            score_elements = score_distribution_section.select('.state_point')
            for element in score_elements:
                score_range = element.select_one('.area_text_score').text.strip()
                percentage = element.select_one('.area_text_percent').text.strip()
                score_distribution[score_range] = percentage

        print(f"Score Distribution: {score_distribution}")

        # 성별 비율 추출
        gender_distribution_section = detail_soup.select_one('.lego_rating_box_change_sex')
        if gender_distribution_section:
            male_percentage = gender_distribution_section.select_one('.type_male .num').text.strip() if gender_distribution_section.select_one('.type_male .num') else 'N/A'
            female_percentage = gender_distribution_section.select_one('.type_female .num').text.strip() if gender_distribution_section.select_one('.type_female .num') else 'N/A'
        else:
            male_percentage = female_percentage = 'N/A'

        print(f"Male Percentage: {male_percentage}%")
        print(f"Female Percentage: {female_percentage}%")


        reviews_section = detail_soup.select('.lego_review_list .area_card')

        reviews = []
        for review in reviews_section:
            # 별점 추출
            rating = review.select_one('.lego_movie_pure_star .area_text_box').text.strip() if review.select_one('.lego_movie_pure_star .area_text_box') else 'N/A'
            
            # 리뷰 내용 추출
            review_text = review.select_one('.area_review_content .desc._text').text.strip() if review.select_one('.area_review_content .desc._text') else 'N/A'
            
            # 작성자 추출
            author = review.select_one('.cm_upload_info .this_text_stress._btn_writer').text.strip() if review.select_one('.cm_upload_info .this_text_stress._btn_writer') else 'N/A'
            
            # 작성일 추출
            date = review.select_one('.cm_upload_info .this_text_normal').text.strip() if review.select_one('.cm_upload_info .this_text_normal') else 'N/A'
            
            # 공감수 추출
            sympathy = review.select_one('.cm_sympathy_area .area_button_upvote .this_text_number').text.strip() if review.select_one('.cm_sympathy_area .area_button_upvote .this_text_number') else '0'
            
            # 비공감수 추출
            non_sympathy = review.select_one('.cm_sympathy_area .area_button_downvote .this_text_number').text.strip() if review.select_one('.cm_sympathy_area .area_button_downvote .this_text_number') else '0'
            
            # 리뷰 정보를 리스트에 추가
            reviews.append({
                'rating': rating,
                'text': review_text,
                'author': author,
                'date': date,
                'sympathy': sympathy,
                'non_sympathy': non_sympathy,
            })
    else:
        real_rating = male_rating = female_rating = 'N/A'
        reviews = []

    # 영화 정보를 저장
    movies.append({
        'title': title,
        'poster_url': poster_url,
        'release_date': release_date,
        'rating': rating,
        'genre': genre,
        'country': country,
        'running_time': running_time,
        'distributor': distributor,
        'description': description,
        'director': directors,
        # 'actors': actors,
        'real_rating': real_rating,
        'male_rating': male_rating,
        'female_rating': female_rating,
        'reviews': reviews
        })

driver.quit()


st.write("영화 정보 목록:")
for movie in movies:
    st.write(movie)
    # st.write(f"{movie['title']}")
    # st.write(f"포스터:")
    # st.write(f"개요: {movie['overview']}")
    # st.write(f"줄거리: {movie['summary']}")
    # st.write(f"개봉일: {movie['release_date']}")
    # st.write(f"등급: {movie['rating']}")
    # st.write(f"장르: {movie['genre']}")
    # st.write(f"국가: {movie['country']}")
    # st.write(f"러닝타임: {movie['running_time']}")
    # st.write(f"배급사: {movie['distributor']}")
    # st.write(f"영화 소개: {movie['description']}")
    # st.write(f"감독: {movie['director']}")
    # st.write(f"출연진: {', '.join(movie['actors'])}")
    # st.write(f"실관람객 평점: {movie['real_rating']}")
    # st.write(f"성별 평점: 남자 - {movie['male_rating']}, 여자 - {movie['female_rating']}")
    # st.write("관람평:")
    for review in movie['reviews']:
        st.write(review)
    # st.write(f" - 평점: {review['score']}, 내용: {review['text']}, 작성자: {review['author']}, 공감: {review['sympathy']}회")
    # st.write("—")