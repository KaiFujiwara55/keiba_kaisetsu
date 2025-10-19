"""
Prompt templates for GPT-5 horse race analysis
"""

SYSTEM_PROMPT = """あなたは競馬データ解析の専門家です。

提供されるデータ:
- レース条件(競馬場、距離、馬場)
- 各馬の過去成績(着順、タイム、着差)
- 騎手実績(勝率、連対率、複勝率)
- 血統情報(父母の成績)

分析時の注意点:
1. データに基づいた客観的分析のみ行う
2. 各馬の強み・弱点を明確に述べる
3. 比較分析では優劣を具体的に示す
4. ランキングでは推奨理由をデータで裏付ける

指定された出力形式に従って分析結果を提供してください。"""

def calculate_parent_stats(horse: dict, parent_type: str) -> dict:
    """
    Calculate parent horse statistics

    Args:
        horse: Horse data dictionary
        parent_type: 'sire' or 'dam'

    Returns:
        Dictionary with total, win_rate, place_rate
    """
    first = horse.get(f'{parent_type}_first', 0)
    second = horse.get(f'{parent_type}_second', 0)
    third = horse.get(f'{parent_type}_third', 0)
    fourth_or_lower = horse.get(f'{parent_type}_fourth_or_lower', 0)

    total = first + second + third + fourth_or_lower

    if total == 0:
        return {
            'total': 0,
            'win_rate': None,
            'place_rate': None
        }

    win_rate = (first / total) * 100
    place_rate = ((first + second + third) / total) * 100

    return {
        'total': total,
        'win_rate': round(win_rate, 1),
        'place_rate': round(place_rate, 1)
    }


def format_race_data(race_data: dict) -> str:
    """
    Format race data for LLM consumption according to LLM_PROMPT.md

    Args:
        race_data: Dictionary containing race and horse information

    Returns:
        Formatted string with race data
    """
    output = []

    # レース情報
    race_id = race_data.get('race_id', '')
    # Use track_name from race_data if available, otherwise extract from race_id
    track_name = race_data.get('track_name', '')

    output.append("# レース情報")
    output.append(f"- 競馬場: {track_name}")
    output.append(f"- レース名: {race_data.get('race_name', '')}")
    output.append(f"- 距離: {race_data.get('distance', '')}")
    output.append(f"- 馬場: {race_data.get('track_type', '')}")
    output.append("")
    output.append("---")
    output.append("")

    # 出走馬データ
    output.append("# 出走馬データ")
    output.append("")

    horses = race_data.get('horses', [])

    for i, horse in enumerate(horses, 1):
        output.append(f"## {i}. {horse.get('horse_name', '')} (枠番: {horse.get('frame_number', '')}, 馬番: {horse.get('horse_number', '')})")
        output.append("")

        # 基本情報
        output.append("### 基本情報")
        days = horse.get('days_since_last_race', 999)
        if days < 999:
            output.append(f"- 前走からの期間: {days}日")
        else:
            output.append("- 前走からの期間: データなし")
        output.append("")

        # 過去成績 (最新5走)
        output.append("### 過去成績 (最新5走)")
        output.append("")
        output.append("| 日付 | 競馬場 | 距離 | 着順 | タイム | 着差 |")
        output.append("|------|--------|------|------|--------|------|")

        recent_results = horse.get('recent_results', [])
        for result in recent_results[:5]:
            date = result.get('date', '-')
            track = result.get('track', '-')
            distance = result.get('distance', '-')
            position = result.get('position', '-')
            time = result.get('time', '-')
            margin = result.get('margin', '-')

            output.append(f"| {date} | {track} | {distance} | {position}着 | {time} | {margin} |")

        # データがない場合
        if not recent_results:
            output.append("| - | - | - | - | - | - |")

        output.append("")

        # 騎手情報
        output.append("### 騎手情報")
        jockey_name = horse.get('jockey_name', '')
        jockey_win_rate = horse.get('jockey_win_rate', 0)
        jockey_place_rate = horse.get('jockey_place_rate', 0)  # 連対率 (1着+2着)
        jockey_show_rate = horse.get('jockey_show_rate', 0)    # 複勝率 (1着+2着+3着)

        if jockey_name:
            output.append(f"- 騎手: {jockey_name}")
            output.append(f"- 勝率: {jockey_win_rate:.1f}%")
            output.append(f"- 連対率: {jockey_place_rate:.1f}%")
            output.append(f"- 複勝率: {jockey_show_rate:.1f}%")
        else:
            output.append("- 騎手: データなし")

        output.append("")

        # 血統情報
        output.append("### 血統情報")
        output.append("")

        # 父馬
        sire_name = horse.get('sire_name', '')
        if sire_name:
            output.append(f"#### 父馬: {sire_name}")

            sire_stats = calculate_parent_stats(horse, 'sire')

            if sire_stats['total'] > 0:
                first = horse.get('sire_first', 0)
                second = horse.get('sire_second', 0)
                third = horse.get('sire_third', 0)
                fourth_or_lower = horse.get('sire_fourth_or_lower', 0)

                output.append(f"- 成績: 1着{first}回、2着{second}回、3着{third}回、4着以下{fourth_or_lower}回 (総戦数: {sire_stats['total']}戦)")

                if sire_stats['win_rate'] is not None:
                    output.append(f"- 勝率: {sire_stats['win_rate']}% | 複勝率: {sire_stats['place_rate']}%")
                else:
                    output.append("- 勝率: データなし | 複勝率: データなし")
            else:
                output.append("- 成績: データなし")
        else:
            output.append("#### 父馬: データなし")

        output.append("")

        # 母馬
        dam_name = horse.get('dam_name', '')
        if dam_name:
            output.append(f"#### 母馬: {dam_name}")

            dam_stats = calculate_parent_stats(horse, 'dam')

            if dam_stats['total'] > 0:
                first = horse.get('dam_first', 0)
                second = horse.get('dam_second', 0)
                third = horse.get('dam_third', 0)
                fourth_or_lower = horse.get('dam_fourth_or_lower', 0)

                output.append(f"- 成績: 1着{first}回、2着{second}回、3着{third}回、4着以下{fourth_or_lower}回 (総戦数: {dam_stats['total']}戦)")

                if dam_stats['win_rate'] is not None:
                    output.append(f"- 勝率: {dam_stats['win_rate']}% | 複勝率: {dam_stats['place_rate']}%")
                else:
                    output.append("- 勝率: データなし | 複勝率: データなし")
            else:
                output.append("- 成績: データなし")
        else:
            output.append("#### 母馬: データなし")

        output.append("")
        output.append("---")
        output.append("")

    return "\n".join(output)


def create_user_prompt(race_data: dict, custom_prompt: str = "") -> str:
    """
    Create user prompt for GPT-5

    Args:
        race_data: Dictionary containing race and horse information
        custom_prompt: Optional custom user instructions

    Returns:
        Formatted user prompt string
    """
    formatted_data = format_race_data(race_data)

    prompt_parts = [formatted_data]

    # Add custom instructions if provided
    if custom_prompt:
        prompt_parts.append("# カスタム指示")
        prompt_parts.append(custom_prompt)
        prompt_parts.append("")

    # Add output format instructions
    prompt_parts.append("# 分析指示")
    prompt_parts.append("")
    prompt_parts.append("上記のデータに基づいて、以下の3つの観点で分析結果を提供してください:")
    prompt_parts.append("")
    prompt_parts.append("## 1. 個別馬分析")
    prompt_parts.append("各馬について、以下の形式で分析してください:")
    prompt_parts.append("")
    prompt_parts.append("### 馬名 (馬番)")
    prompt_parts.append("**強み**")
    prompt_parts.append("- [具体的な強み1]")
    prompt_parts.append("- [具体的な強み2]")
    prompt_parts.append("")
    prompt_parts.append("**弱点**")
    prompt_parts.append("- [具体的な弱点1]")
    prompt_parts.append("- [具体的な弱点2]")
    prompt_parts.append("")
    prompt_parts.append("**総合評価**")
    prompt_parts.append("[総合的なコメント]")
    prompt_parts.append("")
    prompt_parts.append("---")
    prompt_parts.append("")
    prompt_parts.append("## 2. 馬同士の比較")
    prompt_parts.append("注目すべき馬同士の比較分析を行ってください。")
    prompt_parts.append("特に上位候補となる馬について、どの馬が有利かを比較してください。")
    prompt_parts.append("馬名を記載する際は、必ず馬番も併記してください (例: 馬名(馬番))。")
    prompt_parts.append("")
    prompt_parts.append("---")
    prompt_parts.append("")
    prompt_parts.append("## 3. おすすめランキング")
    prompt_parts.append("上位5頭を推奨順にランキングしてください。")
    prompt_parts.append("各馬について、推奨理由を明確に記載してください。")
    prompt_parts.append("")
    prompt_parts.append("### 1位: [馬名] (馬番)")
    prompt_parts.append("**推奨理由**: [データに基づいた理由]")
    prompt_parts.append("")
    prompt_parts.append("### 2位: [馬名] (馬番)")
    prompt_parts.append("**推奨理由**: [データに基づいた理由]")
    prompt_parts.append("")
    prompt_parts.append("(以下同様に5位まで)")

    return "\n".join(prompt_parts)
