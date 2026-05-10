"""
Mirage Studios — Routes Montage Video
Assemblage de scenes, sous-titres et export final.
"""

from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import sys
import json
import uuid
import requests
import tempfile

editing_bp = Blueprint('editing', __name__, url_prefix='/api/editing')

RENDERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'renders')
os.makedirs(RENDERS_DIR, exist_ok=True)


def download_video(url: str, filename: str) -> str:
    """Télécharge une vidéo depuis une URL."""
    filepath = os.path.join(RENDERS_DIR, filename)
    response = requests.get(url, timeout=60)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return filepath


@editing_bp.route('/assemble', methods=['POST', 'OPTIONS'])
@cross_origin()
def assemble_video():
    """Assemble plusieurs vidéos en un seul fichier."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'scenes' not in data:
        return jsonify({"error": "Liste de scènes requise"}), 400

    scenes = data['scenes']
    if not scenes:
        return jsonify({"error": "Aucune scène fournie"}), 400

    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

        clips = []
        temp_files = []

        for i, scene in enumerate(scenes):
            video_url = scene.get('video_url')
            if not video_url:
                continue

            print(f"[Editing] Téléchargement scène {i+1}: {video_url[:50]}")
            filename = f"scene_{uuid.uuid4()}.mp4"
            filepath = download_video(video_url, filename)
            temp_files.append(filepath)

            clip = VideoFileClip(filepath)

            # Ajouter sous-titre si fourni
            subtitle = scene.get('subtitle', '')
            if subtitle:
                txt_clip = TextClip(
                    subtitle,
                    fontsize=28,
                    color='white',
                    bg_color='rgba(0,0,0,0.5)',
                    font='Arial',
                    method='caption',
                    size=(clip.w - 40, None)
                ).set_position(('center', 'bottom')).set_duration(clip.duration)
                clip = CompositeVideoClip([clip, txt_clip])

            clips.append(clip)

        if not clips:
            return jsonify({"error": "Aucune vidéo valide"}), 400

        print(f"[Editing] Assemblage de {len(clips)} scènes...")
        final_clip = concatenate_videoclips(clips, method="compose")

        output_filename = f"mirage_{uuid.uuid4()}.mp4"
        output_path = os.path.join(RENDERS_DIR, output_filename)

        final_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

        # Nettoyer
        for clip in clips:
            clip.close()
        final_clip.close()

        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass

        file_size = os.path.getsize(output_path)
        print(f"[Editing] Film assemblé : {output_filename} ({file_size/1024/1024:.1f}MB)")

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/api/editing/download/{output_filename}",
            "scenes_count": len(clips),
            "file_size_mb": round(file_size/1024/1024, 1),
        })

    except Exception as e:
        print(f"[Editing] Erreur : {e}")
        return jsonify({"error": str(e)}), 500


@editing_bp.route('/download/<filename>', methods=['GET'])
@cross_origin()
def download_video_file(filename):
    """Télécharge le fichier vidéo final."""
    filepath = os.path.join(RENDERS_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Fichier introuvable"}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)


@editing_bp.route('/subtitles', methods=['POST', 'OPTIONS'])
@cross_origin()
def add_subtitles():
    """Ajoute des sous-titres à une vidéo."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'video_url' not in data or 'subtitles' not in data:
        return jsonify({"error": "video_url et subtitles requis"}), 400

    try:
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

        video_url = data['video_url']
        subtitles = data['subtitles']

        filename = f"video_{uuid.uuid4()}.mp4"
        filepath = download_video(video_url, filename)

        clip = VideoFileClip(filepath)
        subtitle_clips = [clip]

        for sub in subtitles:
            text = sub.get('text', '')
            start = sub.get('start', 0)
            end = sub.get('end', clip.duration)

            txt = TextClip(
                text,
                fontsize=26,
                color='white',
                bg_color='black',
                font='Arial',
            ).set_position(('center', 'bottom')).set_start(start).set_end(end)
            subtitle_clips.append(txt)

        final = CompositeVideoClip(subtitle_clips)
        output_filename = f"subtitled_{uuid.uuid4()}.mp4"
        output_path = os.path.join(RENDERS_DIR, output_filename)

        final.write_videofile(output_path, fps=24, verbose=False, logger=None)
        clip.close()
        final.close()
        os.remove(filepath)

        return jsonify({
            "success": True,
            "filename": output_filename,
            "download_url": f"/api/editing/download/{output_filename}",
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@editing_bp.route('/status', methods=['GET'])
@cross_origin()
def editing_status():
    """Vérifie si le module montage est disponible."""
    try:
        import moviepy
        available = True
        version = moviepy.__version__
    except:
        available = False
        version = None

    renders = []
    if os.path.exists(RENDERS_DIR):
        renders = [f for f in os.listdir(RENDERS_DIR) if f.endswith('.mp4')]

    return jsonify({
        "status": "ready" if available else "missing",
        "moviepy_version": version,
        "renders_count": len(renders),
        "features": ["assemble", "subtitles", "download"],
    })