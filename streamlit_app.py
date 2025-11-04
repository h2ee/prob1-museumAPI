# streamlit_app.py
import requests
import streamlit as st

BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1"


def search_artworks(query: str, max_results: int = 10):
    """키워드로 MET API 검색 → objectID 리스트 + 전체 검색 개수 반환"""
    params = {
        "q": query,
        "hasImages": "true",  # 이미지 있는 것만
    }
    resp = requests.get(f"{BASE_URL}/search", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    object_ids = data.get("objectIDs") or []
    total = data.get("total", 0)
    return object_ids[:max_results], total


def get_object_detail(object_id: int):
    """objectID 하나에 대해 상세 정보 가져오기"""
    resp = requests.get(f"{BASE_URL}/objects/{object_id}", timeout=10)
    resp.raise_for_status()
    return resp.json()


def main():
    st.set_page_config(
        page_title="Explore Artworks with MET Museum API",
        layout="wide",
    )

    st.title("Explore Artworks with MET Museum API")
    st.write(
        "Metropolitan Museum of Art의 Open API를 사용해서 "
        "키워드로 작품을 검색하고 이미지를 함께 살펴보는 예제입니다."
    )

    # --- 검색 UI ---
    with st.sidebar:
        st.header("Search")
        query = st.text_input("Keyword", value="flower")
        max_results = st.slider("Number of artworks to show", 1, 20, 5)

        search_button = st.button("Search")

    if search_button and query.strip():
        with st.spinner("Searching MET collection..."):
            try:
                object_ids, total = search_artworks(query.strip(), max_results)
            except Exception as e:
                st.error(f"API 요청 중 오류가 발생했습니다: {e}")
                return

        if not object_ids:
            st.warning(f"검색 결과가 없습니다: “{query}”")
            return

        st.caption(f'Found {total} result(s). Showing top {len(object_ids)} for "{query}".')

        # --- 결과 리스트 렌더링 ---
        for object_id in object_ids:
            try:
                obj = get_object_detail(object_id)
            except Exception:
                continue

            title = obj.get("title", "Untitled")
            artist = obj.get("artistDisplayName") or "Unknown artist"
            date = obj.get("objectDate") or ""
            culture = obj.get("culture") or ""
            medium = obj.get("medium") or ""
            image_url = obj.get("primaryImageSmall") or obj.get("primaryImage")

            with st.container():
                st.markdown(f"### {title}")

                meta_parts = [artist]
                if date:
                    meta_parts.append(date)
                if culture:
                    meta_parts.append(culture)
                if medium:
                    meta_parts.append(medium)

                st.write(" · ".join(meta_parts))

                if image_url:
                    st.image(image_url, use_column_width=True)
                else:
                    st.info("No image available for this artwork.")

                # object 페이지 링크
                object_url = obj.get("objectURL")
                if object_url:
                    st.markdown(f"[View on MET Museum website]({object_url})")

                st.markdown("---")
    else:
        st.info("왼쪽 사이드바에서 키워드를 입력하고 **Search** 버튼을 눌러보세요.")


if __name__ == "__main__":
    main()