"""
競馬レース解析アプリ - Streamlit Application
Netkeiba scraper + GPT-5 analysis for horse racing predictions
"""

import os
import streamlit as st
from datetime import datetime, timedelta

# Streamlit secrets.tomlから環境変数を設定
def setup_environment():
    """
    環境変数をStreamlit secretsから設定
    ローカル環境: .streamlit/secrets.toml
    Streamlit Cloud: Secrets設定
    """
    if hasattr(st, 'secrets'):
        # secrets.tomlから環境変数に設定
        secrets_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'APP_PASSWORD', 'ANALYZER_TYPE']
        for key in secrets_keys:
            if key in st.secrets and not os.getenv(key):
                os.environ[key] = st.secrets[key]

setup_environment()

from scraper.race import RaceScraper
from scraper.horse import HorseScraper
from scraper.jockey import JockeyScraper
from cache.dynamodb import DynamoDBCache
from analyzer.gpt_analyzer import GPTAnalyzer
from analyzer.claude_analyzer import ClaudeAnalyzer


def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔐 ログイン")
        password = st.text_input("パスワードを入力してください", type="password")

        if st.button("ログイン"):
            app_password = os.getenv("APP_PASSWORD", "")
            if password == app_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("パスワードが間違っています")
        st.stop()


def fetch_race_data_with_cache(race_id: str, cache: DynamoDBCache, track_name: str = None) -> dict:
    """
    Fetch complete race data with caching

    Args:
        race_id: Race identifier
        cache: DynamoDB cache instance
        track_name: Track name (e.g., "東京", "中山") - optional, used for accurate track identification

    Returns:
        Complete race data dictionary
    """
    race_scraper = RaceScraper()
    horse_scraper = HorseScraper()
    jockey_scraper = JockeyScraper()

    # Check cache for race metadata
    race_data = cache.get_race_metadata(race_id)

    if not race_data:
        st.info("レース情報を取得中...")
        try:
            race_data = race_scraper.fetch_race_details(race_id, track_name)

            if not race_data:
                st.error("レース情報の取得に失敗しました。レースIDが正しいか確認してください。")
                return None

            # Cache race metadata
            cache.set_race_metadata(race_id, race_data)
        except Exception as e:
            st.error(f"レース情報の取得中にエラーが発生しました: {str(e)}")
            return None

    # Fetch detailed data for each horse
    horses_detailed = []
    total_horses = len(race_data.get('horses', []))

    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, horse in enumerate(race_data.get('horses', [])):
        horse_id = horse['horse_id']
        jockey_id = horse['jockey_id']

        # Show current processing status
        status_text.text(f"馬データ取得中... ({idx + 1}/{total_horses} 完了)")
        progress_bar.progress((idx + 1) / total_horses)

        # Fetch horse results with cache
        horse_results = cache.get_horse_results(horse_id)
        if not horse_results:
            try:
                horse_results = horse_scraper.fetch_horse_results(horse_id)
                if horse_results:
                    cache.set_horse_results(horse_id, horse_results)
            except Exception as e:
                st.warning(f"馬 {horse.get('horse_name', horse_id)} の成績取得に失敗: {str(e)}")
                horse_results = None

        # Fetch parent horses with cache
        parent_horses = cache.get_horse_parents(horse_id)
        if not parent_horses:
            try:
                parent_horses = horse_scraper.fetch_parent_horses(horse_id)
                if parent_horses:
                    cache.set_horse_parents(horse_id, parent_horses)
            except Exception as e:
                st.warning(f"馬 {horse.get('horse_name', horse_id)} の血統情報取得に失敗: {str(e)}")
                parent_horses = None

        # Fetch jockey stats with cache
        jockey_stats = cache.get_jockey_stats(jockey_id)
        if not jockey_stats:
            try:
                jockey_stats = jockey_scraper.fetch_jockey_stats(jockey_id)
                if jockey_stats:
                    cache.set_jockey_stats(jockey_id, jockey_stats)
            except Exception as e:
                st.warning(f"騎手 {horse.get('jockey_name', jockey_id)} の統計取得に失敗: {str(e)}")
                jockey_stats = None

        # Combine all data
        # Extract jockey stats from nested structure
        jockey_overall_stats = jockey_stats.get('overall_stats', {}) if jockey_stats else {}

        horse_detailed = {
            **horse,
            'recent_results': horse_results.get('recent_results', []) if horse_results else [],
            'days_since_last_race': horse_results.get('days_since_last_race', 999) if horse_results else 999,
            'jockey_win_rate': jockey_overall_stats.get('win_rate', 0),
            'jockey_place_rate': jockey_overall_stats.get('place_rate', 0),  # 連対率 (1着+2着)
            'jockey_show_rate': jockey_overall_stats.get('show_rate', 0),    # 複勝率 (1着+2着+3着)
            'sire_name': parent_horses.get('sire', {}).get('name', '') if parent_horses else '',
            'sire_earnings': parent_horses.get('sire', {}).get('earnings', '') if parent_horses else '',
            'sire_first': parent_horses.get('sire', {}).get('first', 0) if parent_horses else 0,
            'sire_second': parent_horses.get('sire', {}).get('second', 0) if parent_horses else 0,
            'sire_third': parent_horses.get('sire', {}).get('third', 0) if parent_horses else 0,
            'sire_fourth_or_lower': parent_horses.get('sire', {}).get('fourth_or_lower', 0) if parent_horses else 0,
            'dam_name': parent_horses.get('dam', {}).get('name', '') if parent_horses else '',
            'dam_earnings': parent_horses.get('dam', {}).get('earnings', '') if parent_horses else '',
            'dam_first': parent_horses.get('dam', {}).get('first', 0) if parent_horses else 0,
            'dam_second': parent_horses.get('dam', {}).get('second', 0) if parent_horses else 0,
            'dam_third': parent_horses.get('dam', {}).get('third', 0) if parent_horses else 0,
            'dam_fourth_or_lower': parent_horses.get('dam', {}).get('fourth_or_lower', 0) if parent_horses else 0
        }

        horses_detailed.append(horse_detailed)

    # Show completion
    progress_bar.progress(1.0)
    status_text.text(f"馬データ取得完了! ({total_horses}/{total_horses} 完了)")

    progress_bar.empty()
    status_text.empty()

    race_data['horses'] = horses_detailed

    # Add track_name if provided
    if track_name:
        race_data['track_name'] = track_name

    return race_data


def main():
    """Main application logic"""
    # Authentication check
    check_authentication()

    # Initialize cache and analyzer
    cache = DynamoDBCache()

    # Select analyzer type (Claude or GPT)
    analyzer_type = os.getenv('ANALYZER_TYPE', 'claude').lower()

    if analyzer_type == 'claude':
        analyzer = ClaudeAnalyzer()
        analyzer_name = "Claude 4.5"
    else:
        analyzer = GPTAnalyzer()
        analyzer_name = "GPT-5"

    # App header
    st.title("🏇 競馬レース解析アプリ")
    st.write(f"netkeibaのデータをスクレイピングし、{analyzer_name}で各馬を分析します")

    # Date selection
    st.subheader("1. レース日を選択")

    # Default to today
    today = datetime.now()

    race_date = st.date_input(
        "レース日",
        value=today,
        min_value=today - timedelta(days=30),
        max_value=today + timedelta(days=30)
    )

    # Format date for netkeiba (YYYYMMDD)
    date_str = race_date.strftime("%Y%m%d")

    # Fetch available races
    if st.button("レース一覧を取得"):
        with st.spinner("レース一覧を取得中..."):
            race_scraper = RaceScraper()
            races = race_scraper.fetch_races_by_date(date_str)

            if races:
                st.session_state.available_races = races
                st.success(f"{len(races)}件のレースが見つかりました")
            else:
                st.error("レースが見つかりませんでした")

    # Track and race number selection
    if 'available_races' in st.session_state and st.session_state.available_races:
        st.subheader("2. 競馬場とレース番号を選択")

        races = st.session_state.available_races

        # Extract unique track names
        track_names = sorted(set(r['track_name'] for r in races))

        selected_track = st.selectbox("競馬場", track_names)

        # Filter races by selected track
        track_races = [r for r in races if r['track_name'] == selected_track]
        race_numbers = sorted(set(r['race_number'] for r in track_races))

        selected_race_number = st.selectbox("レース番号", race_numbers)

        # Find the selected race
        selected_race = next((r for r in track_races if r['race_number'] == selected_race_number), None)

        if selected_race:
            st.info(f"選択: {selected_race['race_name']} (ID: {selected_race['race_id']})")
            st.session_state.selected_race_id = selected_race['race_id']
            st.session_state.selected_track_name = selected_track

    # Custom prompt
    st.subheader("3. カスタムプロンプト (オプション)")
    custom_prompt = st.text_area(
        "追加の分析指示があれば入力してください",
        placeholder="例: 前走からの期間が短い馬を重視してください",
        height=100
    )

    # Cache option
    st.subheader("4. キャッシュ設定")
    use_cache = st.radio(
        "解析結果の利用方法",
        options=["キャッシュを利用 (同じプロンプトなら再利用)", "新規生成 (常に新しく解析)"],
        index=0,
        help="キャッシュを利用すると、同じレース・同じカスタムプロンプトの組み合わせで過去の結果を再利用します"
    )
    force_new_analysis = (use_cache == "新規生成 (常に新しく解析)")

    # Analysis trigger
    st.subheader("5. 解析開始")

    if 'selected_race_id' not in st.session_state:
        st.warning("先にレースを選択してください")
    else:
        if st.button("🚀 解析開始", type="primary"):
            race_id = st.session_state.selected_race_id

            # Get the selected track name from session state
            selected_track_name = st.session_state.get('selected_track_name', None)

            # Check cache first (if not forcing new analysis)
            cached_analysis = None
            if not force_new_analysis:
                with st.spinner("キャッシュを確認中..."):
                    cached_data = cache.get_llm_analysis(race_id, custom_prompt)
                    if cached_data:
                        cached_analysis = cached_data.get('analysis_result')
                        if cached_analysis:
                            st.success("キャッシュから解析結果を取得しました！")

            if cached_analysis:
                # Use cached result
                analysis_result = cached_analysis
                st.session_state.result_displayed = False  # Will be displayed below
            else:
                # Perform new analysis
                if not force_new_analysis:
                    st.info("キャッシュが見つかりませんでした。新規解析を実行します。")
                else:
                    st.info("新規解析を実行します。")

                with st.spinner("データを取得中..."):
                    race_data = fetch_race_data_with_cache(race_id, cache, selected_track_name)

                if not race_data:
                    st.error("データ取得に失敗しました")
                    st.stop()

                st.success(f"データ取得完了: {len(race_data['horses'])}頭")

                st.info(f"{analyzer_name}で解析中...")

                # Create placeholder for streaming output
                st.subheader("6. 解析結果")
                result_placeholder = st.empty()
                accumulated_text = ""
                analysis_result = None

                # Stream the response
                for chunk in analyzer.analyze_horses_stream(race_data, custom_prompt):
                    if chunk['type'] == 'chunk':
                        accumulated_text += chunk['content']
                        result_placeholder.markdown(accumulated_text)
                    elif chunk['type'] == 'final':
                        analysis_result = chunk
                        del analysis_result['type']
                    elif chunk['type'] == 'error':
                        st.error(f"解析に失敗しました: {chunk.get('error', '不明なエラー')}")
                        st.stop()

                if not analysis_result:
                    st.error("解析に失敗しました")
                    st.stop()

                # Save to cache
                cache.set_llm_analysis(race_id, custom_prompt, analysis_result)
                st.success("解析完了！結果をキャッシュに保存しました。")

            # Store results in session
            st.session_state.analysis_result = analysis_result
            # Only mark as displayed if streamed (not from cache)
            if not cached_analysis:
                st.session_state.result_displayed = True

            # Display token usage and cost
            tokens = analysis_result.get('tokens_used', {})
            cost_usd = analysis_result.get('cost_usd', 0)

            # Create info box with cost information
            cache_status = "（キャッシュから取得のためコスト0）" if cached_analysis else "（新規生成）"
            st.info(f"""
            **このアクセスでかかった料金: ${cost_usd:.4f} (約{cost_usd * 150:.2f}円) {cache_status}**

            トークン使用量: 入力 {tokens.get('input', 0):,}, 出力 {tokens.get('output', 0):,}, 合計 {tokens.get('total', 0):,}
            """)

    # Display results (only if not already displayed via streaming or cache)
    if 'analysis_result' in st.session_state and not st.session_state.get('result_displayed', False):
        st.subheader("6. 解析結果")

        result = st.session_state.analysis_result
        st.markdown(result.get('raw_response', 'データなし'))


if __name__ == "__main__":
    # Set page config
    st.set_page_config(
        page_title="競馬レース解析",
        page_icon="🏇",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    main()
