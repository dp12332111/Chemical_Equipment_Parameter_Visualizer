from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from django.core.files.storage import default_storage
from .models import Dataset
from .serializers import SummarySerializer
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter

class UploadCSV(APIView):

    def post(self, request):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        try:
            #validate columns and skip bad lines
            expected_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            df = pd.read_csv(file, on_bad_lines='skip', usecols=range(5))

            if list(df.columns) != expected_columns:
                raise ValueError(f"Invalid columns. Expected: {expected_columns}")

            # Build summary dict
            summary = {
                "total_count": len(df),
                "avg_flowrate": round(df['Flowrate'].mean(), 2),
                "avg_pressure": round(df['Pressure'].mean(), 2),
                "avg_temperature": round(df['Temperature'].mean(), 2),
                "type_distribution": df['Type'].value_counts().to_dict()
            }

            # Save to database
            dataset = Dataset.objects.create(summary=summary, file=file)

            # Keep only the last 5 uploads
            if Dataset.objects.count() > 5:
                oldest = Dataset.objects.order_by('upload_date').first()
                if oldest and oldest.file:
                    default_storage.delete(oldest.file.name)
                oldest.delete()

            return Response({
                'message': 'Upload successful',
                'summary': summary
            }, status=status.HTTP_201_CREATED)

        except pd.errors.ParserError as e:
            return Response({"error": f"CSV parsing error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({"error": f"Missing required column: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class Summary(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = Dataset.objects.order_by('-upload_date').first()
        if not latest:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SummarySerializer(latest.summary)
        return Response(serializer.data)        
    
class History(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datasets = Dataset.objects.order_by('-upload_date')[:5]
        data = [
            {
                'id': ds.id,
                'upload_date': ds.upload_date.isoformat(),
                **ds.summary  # Merge summary dict
            } for ds in datasets
        ]
        return Response(data)


class PDFReport(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest = Dataset.objects.order_by('-upload_date').first()
        if not latest:
            return Response({'error': 'No data available'}, status=status.HTTP_404_NOT_FOUND)
        
        summary = latest.summary
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="chemical_equipment_report.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)  # Standard letter size for better layout
        width, height = letter  # ~612x792 points
        
        # Title
        p.setFont("Helvetica-Bold", 16)
        p.drawCentredString(width / 2, height - 50, "Chemical Equipment Summary Report")
        
        # Reset font for body
        p.setFont("Helvetica", 12)
        
        y = height - 100  # Start below title
        
        # Averages section
        p.drawString(100, y, "Summary Statistics:")
        y -= 30
        p.drawString(100, y, f"Total Equipment Count: {summary['total_count']}")
        y -= 20
        p.drawString(100, y, f"Average Flowrate: {summary['avg_flowrate']:.2f}")
        y -= 20
        p.drawString(100, y, f"Average Pressure: {summary['avg_pressure']:.2f}")
        y -= 20
        p.drawString(100, y, f"Average Temperature: {summary['avg_temperature']:.2f}")
        
        # Type distribution section
        y -= 40  # Extra space between sections
        p.drawString(100, y, "Equipment Type Distribution:")
        y -= 20
        if 'type_distribution' in summary:
            # Sort alphabetically for consistency
            for typ, count in sorted(summary['type_distribution'].items()):
                p.drawString(120, y, f"{typ}: {count}")
                y -= 20
        
        # Add footer
        p.setFont("Helvetica-Oblique", 10)
        p.drawString(100, 50, f"Generated on: {latest.upload_date.strftime('%Y-%m-%d %H:%M:%S')}")
        p.save()
        return response